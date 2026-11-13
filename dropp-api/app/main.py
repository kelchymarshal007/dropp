from fastapi import FastAPI
from app.core.database import engine, Base
from app.models.user import User
from app.models.dropp import Dropp
from app.models.ledger import LedgerEntry
from app.models.post import Post
from app.domain.state_machine import validate_transition
from app.api import dropps

app = FastAPI(title="Dropp Core API", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("SUCCESS: Database connected and all tables created.")

app.include_router(dropps.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "dropp-api"}

@app.post("/test-state-machine")
def test_state_machine(current: str, target: str):
    try:
        validate_transition(current, target)
        return {"status": "ok", "message": f"Valid transition: {current} -> {target}"}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
