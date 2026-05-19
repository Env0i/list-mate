from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_PATH

engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.fetchall()
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA cache_size=-8000")
    cursor.close()


class Base(DeclarativeBase):
    pass


def init_db():
    import app.models  # noqa: F401 — registers all models with Base.metadata
    Base.metadata.create_all(bind=engine)

    # Migration helpers
    def add_col(table, col, typ):
        with engine.connect() as conn:
            result = conn.exec_driver_sql(
                f"SELECT COUNT(*) FROM pragma_table_info('{table}') WHERE name='{col}'"
            )
            if result.scalar() == 0:
                conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
                conn.commit()

    add_col("works", "summary", "VARCHAR")
    add_col("works", "start_date", "VARCHAR")
    add_col("works", "finish_date", "VARCHAR")
    add_col("works", "platform", "VARCHAR")
    add_col("works", "purchase_platform", "VARCHAR")
    add_col("works", "purchase_date", "VARCHAR")
    add_col("works", "purchase_price", "FLOAT")
    add_col("works", "playtime_hours", "FLOAT")
    add_col("works", "replay_count", "INTEGER")
    add_col("works", "priority", "INTEGER")
    add_col("works", "external_links", "VARCHAR")
    add_col("works", "bangumi_data", "VARCHAR")
    add_col("works", "is_free", "BOOLEAN DEFAULT 0")
    with engine.connect() as conn:
        conn.exec_driver_sql("UPDATE works SET is_free = 0 WHERE is_free IS NULL")
        conn.commit()

    # Indexes for foreign keys and common filters
    def add_index(table, col):
        name = f"idx_{table}_{col}"
        with engine.connect() as conn:
            conn.exec_driver_sql(
                f"CREATE INDEX IF NOT EXISTS {name} ON {table}({col})"
            )
            conn.commit()

    add_index("game_profiles", "work_id")
    add_index("work_tags", "work_id")
    add_index("work_tags", "tag_id")
    add_index("timeline_entries", "work_id")
    add_index("attachments", "game_profile_id")
    add_index("works", "updated_at")
    add_index("works", "category")
    add_index("works", "status")
    add_index("game_profiles", "status")
    add_index("timeline_entries", "created_at")

    # GameProfile 扩展字段
    add_col("game_profiles", "progress_type", "VARCHAR")
    add_col("game_profiles", "start_date", "VARCHAR")
    add_col("game_profiles", "finish_date", "VARCHAR")
    add_col("game_profiles", "playtime_hours", "FLOAT")
    add_col("game_profiles", "source", "VARCHAR")
    add_col("game_profiles", "mods_list", "VARCHAR")
    add_col("game_profiles", "notes", "VARCHAR")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
