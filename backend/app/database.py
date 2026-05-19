from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_PATH

engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


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
