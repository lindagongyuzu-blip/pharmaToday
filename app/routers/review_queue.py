from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import ReviewQueue, QueueStatus
from app.schemas.user import ReviewQueueResponse

router = APIRouter(prefix="/review_queue", tags=["Review Queue"])

@router.get("", response_model=List[ReviewQueueResponse])
def get_review_queue(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(ReviewQueue)
    if user_id is not None:
        query = query.filter(ReviewQueue.user_id == user_id)
        
    return query.all()

@router.post("/{queue_id}/complete", response_model=ReviewQueueResponse)
def complete_review_queue_item(queue_id: int, db: Session = Depends(get_db)):
    item = db.query(ReviewQueue).filter(ReviewQueue.id == queue_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="ReviewQueue item not found")
        
    # Only update status
    item.status = QueueStatus.COMPLETED
    db.commit()
    db.refresh(item)
    return item

from app.logic.review_queue_service import reopen_review_queue_item_service

@router.post("/{queue_id}/reopen", response_model=ReviewQueueResponse)
def reopen_review_queue_item_endpoint(queue_id: int, db: Session = Depends(get_db)):
    item = reopen_review_queue_item_service(queue_id, db)
    if not item:
        raise HTTPException(status_code=404, detail="ReviewQueue item not found")
    return item
