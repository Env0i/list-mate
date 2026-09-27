"""
Zace — 全自动部署脚本
用法: python deploy.py

功能:
  1. 构建前端 (vite build)
  2. 上传 dist → 服务器 /www/Zace/dist/
  3. 上传 backend/ → 服务器 /www/Zace/backend/（排除 venv/__pycache__）
  4. 服务器上创建 venv + pip install
  5. 创建 systemd 服务 (zace.service)
  6. 创建 Nginx 配置 (端口 8081, API 代理至 8002) 并重启服务
"""
import os, sys, time
import paramiko
import httpx

# ─── 配置 ────────────────────────────────────────────────────
HOST = "47.108.188.175"
KEY = "C:/Users/29522/.ssh/money-mate.pem"
USER = "root"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REMOTE_ROOT = "/www/Zace"

FRONTEND_SRC = os.path.join(PROJECT_ROOT, "frontend")
BACKEND_SRC = os.path.join(PROJECT_ROOT, "backend")

REMOTE_DIST = f"{REMOTE_ROOT}/dist"
REMOTE_BACKEND = f"{REMOTE_ROOT}/backend"
REMOTE_VENV = f"{REMOTE_ROOT}/venv"

NGINX_CONF = f"{REMOTE_ROOT}/zace.conf"
NGINX_TARGET = "/etc/nginx/conf.d/zace.conf"
SERVICE_FILE = f"{REMOTE_ROOT}/zace.service"
SERVICE_TARGET = "/etc/systemd/system/zace.service"


# ─── 第 1 步: 构建前端 ─────────────────────────────────────
def build_frontend():
    print("=" * 50)
    print("1/6  构建前端...")
    os.chdir(FRONTEND_SRC)
    ret = os.system("npx vite build")
    if ret != 0:
        print("!! 构建失败")
        sys.exit(1)
    print("  前端构建完成")
    os.chdir(PROJECT_ROOT)


# ─── 第 2 步: SSH 连接 ──────────────────────────────────────
def connect():
    print("=" * 50)
    print("2/6  连接服务器...")
    key = paramiko.RSAKey.from_private_key_file(KEY)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, pkey=key, timeout=10)
    print("  连接成功")
    return client


# ─── 第 3 步: 上传前端 ──────────────────────────────────────
def upload_frontend(client, sftp):
    print("=" * 50)
    print("3/6  上传前端 dist...")
    # 先清空远端旧产物：vite 产物带 hash，旧资源会无限累积
    _run(client, f"rm -rf {REMOTE_DIST}")
    local_dist = os.path.join(FRONTEND_SRC, "dist")
    _upload_dir(sftp, local_dist, REMOTE_DIST)


# ─── 第 4 步: 上传后端 ──────────────────────────────────────
def upload_backend(sftp):
    print("=" * 50)
    print("4/6  上传后端代码...")
    _upload_dir(sftp, BACKEND_SRC, REMOTE_BACKEND, ignore=[
        "venv", "__pycache__", ".venv", "*.pyc", ".pytest_cache",
        "list_mate.db", "list_mate.db-shm", "list_mate.db-wal",
        "bangumi_cache", "server.log",
        "fix_game_status.py",  # 一次性数据清洗脚本，误运行会改服务器数据
    ])


def _upload_dir(sftp, local_dir, remote_dir, ignore=None):
    """递归上传目录，自动创建远端目录"""
    count = 0
    for root, dirs, files in os.walk(local_dir):
        # 过滤掉忽略的目录
        if ignore:
            dirs[:] = [d for d in dirs if d not in ignore]
            files = [f for f in files if f not in ignore and not any(
                f.endswith(i.replace("*", "")) for i in ignore if "*" in i
            )]

        rel = os.path.relpath(root, local_dir)
        cur_remote = remote_dir if rel == "." else f"{remote_dir}/{rel.replace(os.sep, '/')}"

        # 创建远端目录
        try:
            sftp.stat(cur_remote)
        except FileNotFoundError:
            parts = cur_remote.replace(remote_dir, "").strip("/").split("/")
            p = remote_dir
            for part in parts:
                p += "/" + part
                try:
                    sftp.stat(p)
                except FileNotFoundError:
                    sftp.mkdir(p)

        # 上传文件
        for f in files:
            local_path = os.path.join(root, f)
            remote_path = f"{cur_remote}/{f}"
            sftp.put(local_path, remote_path)
            count += 1
            sys.stdout.write(f"\r  已上传 {count} 个文件")
            sys.stdout.flush()

    print(f"\n  上传完成: {count} 个文件")


# ─── 第 5 步: 服务器安装依赖 ────────────────────────────────
def setup_server(client):
    print("=" * 50)
    print("5/6  服务器安装依赖...")

    # 创建 venv（如果没有），用 python3.8 确保兼容
    cmd = f"""
    if [ ! -d "{REMOTE_VENV}" ]; then
        python3.8 -m venv {REMOTE_VENV}
        echo "  venv created with python3.8"
    else
        echo "  venv already exists"
    fi
    """
    _run(client, cmd)

    # 安装依赖（包含 eval_type_backport 和 python-multipart）
    cmd = f"""
    cd {REMOTE_BACKEND}
    {REMOTE_VENV}/bin/pip install -r requirements.txt -q
    echo "  dependencies installed"
    """
    _run(client, cmd)


# ─── 第 6 步: 创建 Nginx 配置 + systemd 服务 ───────────────
def setup_configs(client):
    print("=" * 50)
    print("6/6  创建 Nginx 配置 + systemd 服务...")

    # --- Nginx 配置 ---
    nginx_conf = """server {
    listen 8081;
    server_name 47.108.188.175;
    index index.html;
    root /www/Zace/dist;
    access_log /www/wwwlogs/zace.log;
    error_log /www/wwwlogs/zace.error.log;

    location / {
        try_files $uri $uri/ /index.html;
        expires -1;
        add_header Cache-Control "no-cache, must-revalidate";
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50m;
    }
}
"""
    # 写入临时文件再 cp（避免远端无编辑器）
    stdin, stdout, stderr = client.exec_command(f"cat > {NGINX_CONF} << 'NGINXEOF'\n{nginx_conf}\nNGINXEOF")
    stdout.channel.recv_exit_status()
    _run(client, f"cp {NGINX_CONF} {NGINX_TARGET}")
    print("  Nginx 配置已创建")

    # --- systemd 服务 ---
    service = f"""[Unit]
Description=Zace Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={REMOTE_BACKEND}
ExecStart={REMOTE_VENV}/bin/uvicorn app.main:app --host 127.0.0.1 --port 8002
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
StandardOutput=append:/www/wwwlogs/zace_backend.log
StandardError=append:/www/wwwlogs/zace_backend.error.log

[Install]
WantedBy=multi-user.target
"""
    stdin, stdout, stderr = client.exec_command(f"cat > {SERVICE_FILE} << 'SVCEOF'\n{service}\nSVCEOF")
    stdout.channel.recv_exit_status()
    _run(client, f"cp {SERVICE_FILE} {SERVICE_TARGET}")
    print("  systemd 服务已创建")

    # 重启服务
    print("  重启服务...")
    _run(client, "systemctl daemon-reload")
    _run(client, "systemctl enable zace.service")
    _run(client, "systemctl restart zace.service")
    _run(client, "nginx -s reload")
    print("  健康检查（经 Nginx 公网链路）...")
    for i in range(12):  # retry for up to 60 seconds
        time.sleep(5)
        try:
            # 原先打的 127.0.0.1:8002 是部署机自己的回环地址（uvicorn 的
            # 127.0.0.1 属于服务器），本地脚本永远连不上；改走 Nginx 公网入口
            resp = httpx.get(f"http://{HOST}:8081/api/works?page_size=1", timeout=5)
            if resp.status_code == 200:
                print("  ✓ API 健康检查通过")
                break
        except Exception:
            pass
        if i == 11:
            print("  ⚠ API 健康检查未通过，请检查服务状态")
    print("  服务已重启")


def _run(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err:
        # pip install 的 warning 不算错误
        if "error" in err.lower() or "traceback" in err.lower():
            print("  ERR:", err)
    return out, err


# ─── 主流程 ──────────────────────────────────────────────────
def main():
    build_frontend()

    client = connect()
    sftp = client.open_sftp()

    # 创建远端根目录
    try:
        sftp.stat(REMOTE_ROOT)
    except FileNotFoundError:
        sftp.mkdir(REMOTE_ROOT)
        print(f"  创建 {REMOTE_ROOT}")

    upload_frontend(client, sftp)
    upload_backend(sftp)
    sftp.close()

    setup_server(client)
    setup_configs(client)

    client.close()

    print("=" * 50)
    print("[OK] 部署完成!")
    print(f"   前端: http://{HOST}:8081")
    print(f"   API:  http://{HOST}:8081/api/works")
    print("=" * 50)


if __name__ == "__main__":
    main()
