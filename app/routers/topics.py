from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.fact import Topic
from app.schemas.fact import TopicCreate, TopicResponse

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.post("", response_model=TopicResponse)
def create_topic(topic_in: TopicCreate, db: Session = Depends(get_db)):
    db_topic = Topic(**topic_in.model_dump())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

@router.get("", response_model=List[TopicResponse])
def get_topics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    topics = db.query(Topic).offset(skip).limit(limit).all()
    return topics

@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic
