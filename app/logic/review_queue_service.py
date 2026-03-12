from sqlalchemy.orm import Session
from app.models.user import ReviewQueue, QueueStatus

def reopen_review_queue_item_service(queue_id: int, db: Session):
    item = db.query(ReviewQueue).filter(ReviewQueue.id == queue_id).first()
    if not item:
        return None
        
    try:
        if item.status == QueueStatus.COMPLETED:
            item.status = QueueStatus.PENDING
            
        db.commit()
        db.refresh(item)
        return item
    except Exception as e:
        db.rollback()
        raise e
