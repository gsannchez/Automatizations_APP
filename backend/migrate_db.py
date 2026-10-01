from sqlalchemy import text
from app.core.database import sync_engine

def migrate():
    with sync_engine.connect() as conn:
        print("Migrating database...")
        # Añadir user_id a channel
        conn.execute(text('ALTER TABLE channel ADD COLUMN IF NOT EXISTS user_id UUID'))
        # Añadir progress a video
        conn.execute(text('ALTER TABLE video ADD COLUMN IF NOT EXISTS progress INTEGER DEFAULT 0'))
        # También asegurar que la tabla user_settings existe
        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
