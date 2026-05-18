<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { gameProfilesApi } from '../api/client'

const route = useRoute()
const router = useRouter()

const form = ref({ name: '本体', status: 'wish' })
const saving = ref(false)
const error = ref('')

async function submit() {
  if (!form.value.name.trim()) {
    error.value = '请输入配置名称'
    return
  }
  saving.value = true
  error.value = ''
  try {
    const { data } = await gameProfilesApi.create(route.params.id, form.value)
    router.push(`/works/${route.params.id}/game-profiles/${data.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || '创建失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="page-inner">
      <div class="hd-row">
        <button class="back-btn" @click="router.back()">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd"/>
          </svg>
          返回
        </button>
      </div>

      <h1 class="page-title">新增游戏配置</h1>

      <div class="form">
        <div class="field">
          <label class="label">配置名称</label>
          <input v-model="form.name" type="text" class="inp" placeholder="如：本体、整合包、自打模组" />
        </div>

        <div class="field">
          <label class="label">初始状态</label>
          <div class="status-row">
            <button
              v-for="opt in [
                { key: 'wish', label: '想玩' }, { key: 'playing', label: '在玩' },
                { key: 'completed', label: '通关' }, { key: 'dropped', label: '弃坑' },
                { key: 'wait_buy', label: '等购买' }, { key: 'wait_sale', label: '等折扣' },
              ]"
              :key="opt.key"
              class="st-opt"
              :class="{ on: form.status === opt.key }"
              @click="form.status = opt.key"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button class="save-btn" @click="submit" :disabled="saving">
          {{ saving ? '创建中...' : '创建配置' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 20px 16px; }
@media (min-width: 768px) { .page { padding: 24px 32px; } }
.page-inner { max-width: 500px; margin: 0 auto; }

.hd-row { margin-bottom: 20px; }
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: all 0.15s;
}
.back-btn:hover { color: var(--text-primary); background: var(--bg-surface-hover); }

.page-title { font-size: var(--fs-2xl); font-weight: 800; margin-bottom: 28px; }

.form { display: flex; flex-direction: column; gap: 20px; }
.field { }
.label {
  display: block;
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.inp { width: 100%; }

.status-row { display: flex; flex-wrap: wrap; gap: 6px; }
.st-opt {
  height: 30px;
  padding: 0 14px;
  border-radius: var(--radius-full);
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  background: var(--bg-surface);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
}
.st-opt:hover { border-color: var(--text-tertiary); }
.st-opt.on {
  background: var(--primary);
  color: white;
  border-color: transparent;
}

.error { font-size: var(--fs-sm); color: var(--c-anime); }

.save-btn {
  width: 100%;
  height: 42px;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: white;
  font-size: var(--fs-base);
  font-weight: 700;
  transition: all 0.15s;
}
.save-btn:hover { background: var(--primary-hover); }
.save-btn:disabled { opacity: 0.5; cursor: default; }
</style>
