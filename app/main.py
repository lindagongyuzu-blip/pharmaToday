from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.routers import topics, claims, evidence, judgments, review_queue

app = FastAPI(title="Pharma Intelligence Reasoning Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router)
app.include_router(claims.router)
app.include_router(evidence.router)
app.include_router(judgments.router)
app.include_router(review_queue.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def health_db_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "db": str(e)})
