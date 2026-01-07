from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Dict
from app.database import get_db
from app import models, schemas, auth
from collections import defaultdict

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Calculate streak (consecutive days with at least one completed quiz)
    today = datetime.utcnow().date()
    streak = 0
    check_date = today
    
    while True:
        day_start = datetime.combine(check_date, datetime.min.time())
        day_end = datetime.combine(check_date, datetime.max.time())
        
        has_activity = db.query(models.QuizSession).filter(
            and_(
                models.QuizSession.user_id == current_user.id,
                models.QuizSession.completed_at.isnot(None),
                models.QuizSession.completed_at >= day_start,
                models.QuizSession.completed_at <= day_end
            )
        ).first()
        
        if has_activity:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Today's completed questions
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    today_sessions = db.query(models.QuizSession).filter(
        and_(
            models.QuizSession.user_id == current_user.id,
            models.QuizSession.completed_at.isnot(None),
            models.QuizSession.completed_at >= today_start,
            models.QuizSession.completed_at <= today_end
        )
    ).all()
    
    today_completed = 0
    for session in today_sessions:
        answers = db.query(models.Answer).filter(
            models.Answer.session_id == session.id
        ).count()
        today_completed += answers
    
    today_goal = 5  # Default goal, can be made configurable later
    
    # Total answered and accuracy
    all_answers = db.query(models.Answer).join(models.QuizSession).filter(
        models.QuizSession.user_id == current_user.id
    ).all()
    
    total_answered = len(all_answers)
    correct_answers = sum(1 for a in all_answers if a.is_correct)
    accuracy = (correct_answers / total_answered * 100) if total_answered > 0 else 0.0
    
    return schemas.DashboardStats(
        streak=streak,
        today_completed=today_completed,
        today_goal=today_goal,
        total_answered=total_answered,
        accuracy=round(accuracy, 1)
    )


@router.get("/topics/{topic_id}", response_model=schemas.TopicProgress)
def get_topic_progress(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    progress = db.query(models.UserProgress).filter(
        and_(
            models.UserProgress.user_id == current_user.id,
            models.UserProgress.topic_id == topic_id
        )
    ).first()
    
    if not progress:
        # Return default progress if none exists
        return schemas.TopicProgress(
            topic_id=topic_id,
            mastery_percentage=0.0,
            questions_answered=0,
            last_updated=datetime.utcnow()
        )
    
    return progress


@router.get("/map", response_model=schemas.MapResponse)
def get_knowledge_map(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get all topics grouped by level/cluster
    all_topics = db.query(models.Topic).order_by(models.Topic.level, models.Topic.id).all()
    
    # Get user progress for all topics
    user_progress = {
        p.topic_id: p
        for p in db.query(models.UserProgress).filter(
            models.UserProgress.user_id == current_user.id
        ).all()
    }
    
    # Group topics by a simple cluster (for now, by first letter or level)
    # In a real app, you'd have a Cluster/Group model
    clusters_dict: Dict[str, Dict[str, List]] = defaultdict(lambda: defaultdict(list))
    
    for topic in all_topics:
        # Use level as cluster key, or "General" if no level
        cluster_key = topic.level or "General"
        level_key = topic.level or "A0"
        
        progress = user_progress.get(topic.id)
        mastery = progress.mastery_percentage if progress else 0.0
        
        # Determine status
        if mastery >= 100:
            status = "completed"
        elif mastery > 0:
            status = "active"
        else:
            # Check prerequisites
            if topic.prerequisite_topic_id:
                prereq_progress = user_progress.get(topic.prerequisite_topic_id)
                if not prereq_progress or prereq_progress.mastery_percentage < 100:
                    status = "locked"
                else:
                    status = "active"
            else:
                status = "active"
        
        clusters_dict[cluster_key][level_key].append(schemas.MapNode(
            id=topic.id,
            title=topic.title,
            status=status,
            mastery=mastery
        ))
    
    # Convert to response format
    clusters = []
    cluster_id = 1
    
    for cluster_title, levels_dict in clusters_dict.items():
        levels = []
        for level_name, nodes in sorted(levels_dict.items()):
            level_mastery = sum(n.mastery for n in nodes) / len(nodes) if nodes else 0.0
            levels.append(schemas.MapLevel(
                level=level_name,
                nodes=nodes,
                mastery=round(level_mastery, 1)
            ))
        
        clusters.append(schemas.MapCluster(
            id=cluster_id,
            title=cluster_title,
            levels=levels
        ))
        cluster_id += 1
    
    return schemas.MapResponse(clusters=clusters)
