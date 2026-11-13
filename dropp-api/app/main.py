from fastapi import FastAPI
from app.core.database import engine, Base

app = FastAPI(title="Dropp Core API", version="1.0.0")

@app.on_event("startup")
async def startup():
    # In production, use Alembic. For now, create tables on startup.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected and tables created.")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "dropp-api"}
