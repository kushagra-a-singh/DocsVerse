from sqlalchemy import create_engine, text

from backend.app.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text("UPDATE documents SET status = LOWER(status);"))
    conn.commit()
    print("All document status values updated to lowercase.")
