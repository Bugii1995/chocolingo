from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.schemas import (
    TopicCreate,
    TopicUpdate,
    TopicAdminResponse,
)
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/admin/topics",
    tags=["admin-topics"],
)

def require_admin(user: models.User = Depends(get_current_user)):
    # FINAL:
    # if user.role not in ("admin", "superadmin"):
    #     raise HTTPException(status_code=403, detail="Not authorized")
    return user


@router.post(
    "",
    response_model=TopicAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_topic(
    data: TopicCreate,
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    # Validate prerequisite topic if provided
    if data.prerequisite_topic_id:
        prerequisite = db.query(models.Topic).filter_by(id=data.prerequisite_topic_id).first()
        if not prerequisite:
            raise HTTPException(status_code=404, detail="Prerequisite topic not found")

    topic = models.Topic(
        title=data.title,
        description=data.description,
        level=data.level,
        prerequisite_topic_id=data.prerequisite_topic_id,
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    # Get question count
    question_count = db.query(func.count(models.Question.id)).filter(
        models.Question.topic_id == topic.id
    ).scalar()

    return TopicAdminResponse(
        id=topic.id,
        title=topic.title,
        description=topic.description,
        level=topic.level,
        prerequisite_topic_id=topic.prerequisite_topic_id,
        question_count=question_count,
    )


@router.get(
    "",
    response_model=list[TopicAdminResponse],
)
def list_topics(
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    topics = db.query(models.Topic).all()
    
    result = []
    for topic in topics:
        question_count = db.query(func.count(models.Question.id)).filter(
            models.Question.topic_id == topic.id
        ).scalar()
        
        result.append(TopicAdminResponse(
            id=topic.id,
            title=topic.title,
            description=topic.description,
            level=topic.level,
            prerequisite_topic_id=topic.prerequisite_topic_id,
            question_count=question_count,
        ))
    
    return result


@router.get(
    "/{topic_id}",
    response_model=TopicAdminResponse,
)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    topic = db.query(models.Topic).filter_by(id=topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get question count
    question_count = db.query(func.count(models.Question.id)).filter(
        models.Question.topic_id == topic.id
    ).scalar()

    return TopicAdminResponse(
        id=topic.id,
        title=topic.title,
        description=topic.description,
        level=topic.level,
        prerequisite_topic_id=topic.prerequisite_topic_id,
        question_count=question_count,
    )


@router.put(
    "/{topic_id}",
    response_model=TopicAdminResponse,
)
def update_topic(
    topic_id: int,
    data: TopicUpdate,
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    topic = db.query(models.Topic).filter_by(id=topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Validate prerequisite topic if provided
    if data.prerequisite_topic_id is not None:
        if data.prerequisite_topic_id == topic_id:
            raise HTTPException(
                status_code=400,
                detail="Topic cannot be its own prerequisite"
            )
        if data.prerequisite_topic_id:
            prerequisite = db.query(models.Topic).filter_by(id=data.prerequisite_topic_id).first()
            if not prerequisite:
                raise HTTPException(status_code=404, detail="Prerequisite topic not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(topic, field, value)

    db.commit()
    db.refresh(topic)

    # Get question count
    question_count = db.query(func.count(models.Question.id)).filter(
        models.Question.topic_id == topic.id
    ).scalar()

    return TopicAdminResponse(
        id=topic.id,
        title=topic.title,
        description=topic.description,
        level=topic.level,
        prerequisite_topic_id=topic.prerequisite_topic_id,
        question_count=question_count,
    )


@router.delete(
    "/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    topic = db.query(models.Topic).filter_by(id=topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Check if topic has questions
    question_count = db.query(func.count(models.Question.id)).filter(
        models.Question.topic_id == topic.id
    ).scalar()
    
    if question_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete topic with {question_count} question(s). Delete or move questions first."
        )

    db.delete(topic)
    db.commit()
    return
