from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.schemas import (
    QuestionCreate,
    QuestionUpdate,
    QuestionAdminResponse,
    PaginatedQuestionsResponse,
)
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/admin/questions",
    tags=["admin-questions"],
)

def require_admin(user: models.User = Depends(get_current_user)):
    # FINAL:
    # if user.role not in ("admin", "superadmin"):
    #     raise HTTPException(status_code=403, detail="Not authorized")
    return user


@router.post(
    "",
    response_model=QuestionAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    topic = db.query(models.Topic).filter_by(id=data.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    question = models.Question(
        topic_id=data.topic_id,
        prompt=data.prompt,
        question_type=data.question_type.value.upper(),
        choices=data.choices,
        correct_answer=data.correct_answer,
        explanation=data.explanation,
        hint=data.hint,
        difficulty=data.difficulty,
        tags=data.tags,
        is_active=data.is_active,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


@router.get(
    "",
    response_model=PaginatedQuestionsResponse,
)
def list_questions(
    topic_id: int | None = Query(None, alias="topic_id"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    query = db.query(models.Question)

    if topic_id:
        query = query.filter(models.Question.topic_id == topic_id)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    items = query.order_by(models.Question.created_at.desc()).offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedQuestionsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{question_id}",
    response_model=QuestionAdminResponse,
)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    question = db.query(models.Question).filter_by(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return question


@router.put(
    "/{question_id}",
    response_model=QuestionAdminResponse,
)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    question = db.query(models.Question).filter_by(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    for field, value in data.dict(exclude_unset=True).items():
        if field == "question_type":
            value = value.value.upper()
        setattr(question, field, value)

    db.commit()
    db.refresh(question)

    return question


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def disable_question(
    question_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    question = db.query(models.Question).filter_by(id=question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question.is_active = False
    db.commit()
    return
