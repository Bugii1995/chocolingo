from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.schemas import AdminDashboardStats
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/admin/dashboard",
    tags=["admin-dashboard"],
)

def require_admin(user: models.User = Depends(get_current_user)):
    # FINAL:
    # if user.role not in ("admin", "superadmin"):
    #     raise HTTPException(status_code=403, detail="Not authorized")
    return user


@router.get(
    "",
    response_model=AdminDashboardStats,
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    user = Depends(require_admin),
):
    # Count topics
    total_topics = db.query(func.count(models.Topic.id)).scalar()

    # Count questions
    total_questions = db.query(func.count(models.Question.id)).scalar()
    active_questions = db.query(func.count(models.Question.id)).filter(
        models.Question.is_active == True
    ).scalar()
    inactive_questions = total_questions - active_questions

    # Count users
    total_users = db.query(func.count(models.User.id)).scalar()

    return AdminDashboardStats(
        total_topics=total_topics or 0,
        total_questions=total_questions or 0,
        active_questions=active_questions or 0,
        inactive_questions=inactive_questions or 0,
        total_users=total_users or 0,
    )
