from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("/", response_model=List[schemas.TopicResponse])
def list_topics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    topics = db.query(models.Topic).all()
    return topics


@router.get("/{topic_id}", response_model=schemas.TopicResponse)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    return topic
