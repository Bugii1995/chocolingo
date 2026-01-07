from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List
from app.database import get_db
from app import models, schemas, auth
import random

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.post("/sessions", response_model=schemas.QuizSessionResponse, status_code=status.HTTP_201_CREATED)
def create_quiz_session(
    session_data: schemas.QuizSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify topic exists
    topic = db.query(models.Topic).filter(models.Topic.id == session_data.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check if topic is unlocked (for now, allow all - can add prerequisite logic later)
    
    # Get questions for this topic
    questions = db.query(models.Question).filter(
        models.Question.topic_id == session_data.topic_id
    ).all()
    
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions available for this topic"
        )
    
    # Create quiz session
    quiz_session = models.QuizSession(
        user_id=current_user.id,
        topic_id=session_data.topic_id,
        mode=session_data.mode
    )
    db.add(quiz_session)
    db.commit()
    db.refresh(quiz_session)
    
    # Return questions without correct answers
    question_responses = []
    for q in questions:
        question_responses.append(schemas.QuestionResponse(
            id=q.id,
            topic_id=q.topic_id,
            prompt=q.prompt,
            question_type=q.question_type,
            choices=q.choices
        ))
    
    return schemas.QuizSessionResponse(
        id=quiz_session.id,
        user_id=quiz_session.user_id,
        topic_id=quiz_session.topic_id,
        mode=quiz_session.mode,
        started_at=quiz_session.started_at,
        completed_at=quiz_session.completed_at,
        score=quiz_session.score,
        questions=question_responses
    )


@router.get("/sessions/{session_id}", response_model=schemas.QuizSessionResponse)
def get_quiz_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    session = db.query(models.QuizSession).filter(
        and_(
            models.QuizSession.id == session_id,
            models.QuizSession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz session not found"
        )
    
    # Get questions for this session's topic
    questions = db.query(models.Question).filter(
        models.Question.topic_id == session.topic_id
    ).all()
    
    question_responses = []
    for q in questions:
        question_responses.append(schemas.QuestionResponse(
            id=q.id,
            topic_id=q.topic_id,
            prompt=q.prompt,
            question_type=q.question_type,
            choices=q.choices
        ))
    
    return schemas.QuizSessionResponse(
        id=session.id,
        user_id=session.user_id,
        topic_id=session.topic_id,
        mode=session.mode,
        started_at=session.started_at,
        completed_at=session.completed_at,
        score=session.score,
        questions=question_responses
    )


@router.post("/sessions/{session_id}/answers", response_model=schemas.QuizResultsResponse)
def submit_answers(
    session_id: int,
    answers_data: schemas.AnswersSubmit,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get session and verify ownership
    session = db.query(models.QuizSession).filter(
        and_(
            models.QuizSession.id == session_id,
            models.QuizSession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz session not found"
        )
    
    # Check if already completed
    if session.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz session already completed"
        )
    
    # Get all questions for this topic
    questions = {q.id: q for q in db.query(models.Question).filter(
        models.Question.topic_id == session.topic_id
    ).all()}
    
    # Check if answers already exist (prevent resubmission)
    existing_answers = db.query(models.Answer).filter(
        models.Answer.session_id == session_id
    ).all()
    
    if existing_answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers already submitted for this session"
        )
    
    # Validate and process answers
    correct_count = 0
    answer_responses = []
    
    for answer_data in answers_data.answers:
        question = questions.get(answer_data.question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {answer_data.question_id} not found in this topic"
            )
        
        # Check if answer already exists for this question
        existing = db.query(models.Answer).filter(
            and_(
                models.Answer.session_id == session_id,
                models.Answer.question_id == answer_data.question_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Answer already submitted for question {answer_data.question_id}"
            )
        
        # Validate answer (backend is authority)
        is_correct = False
        if question.question_type == models.QuestionType.MULTIPLE_CHOICE:
            is_correct = answer_data.user_answer.strip().lower() == question.correct_answer.strip().lower()
        elif question.question_type == models.QuestionType.FILL_BLANK:
            # Case-insensitive comparison for fill-in-the-blank
            is_correct = answer_data.user_answer.strip().lower() == question.correct_answer.strip().lower()
        
        if is_correct:
            correct_count += 1
        
        # Create answer record
        answer = models.Answer(
            session_id=session_id,
            question_id=answer_data.question_id,
            user_answer=answer_data.user_answer,
            is_correct=is_correct
        )
        db.add(answer)
        db.flush()  # Flush to get the answer ID
        answer_responses.append(schemas.AnswerResponse(
            id=answer.id,
            question_id=answer.question_id,
            user_answer=answer.user_answer,
            is_correct=answer.is_correct,
            submitted_at=answer.submitted_at,
            correct_answer=question.correct_answer
        ))
    
    # Calculate score
    total_questions = len(questions)
    score = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    # Update session
    session.completed_at = datetime.utcnow()
    session.score = score
    
    # Update or create user progress
    progress = db.query(models.UserProgress).filter(
        and_(
            models.UserProgress.user_id == current_user.id,
            models.UserProgress.topic_id == session.topic_id
        )
    ).first()
    
    if progress:
        # Update existing progress
        progress.questions_answered += total_questions
        # Recalculate mastery based on all answers for this topic
        all_answers = db.query(models.Answer).join(models.QuizSession).filter(
            and_(
                models.QuizSession.user_id == current_user.id,
                models.QuizSession.topic_id == session.topic_id
            )
        ).all()
        if all_answers:
            correct_answers = sum(1 for a in all_answers if a.is_correct)
            progress.mastery_percentage = (correct_answers / len(all_answers) * 100)
        progress.last_updated = datetime.utcnow()
    else:
        # Create new progress
        progress = models.UserProgress(
            user_id=current_user.id,
            topic_id=session.topic_id,
            questions_answered=total_questions,
            mastery_percentage=score
        )
        db.add(progress)
    
    db.commit()
    
    return schemas.QuizResultsResponse(
        session_id=session.id,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_count,
        answers=answer_responses,
        topic_mastery=progress.mastery_percentage
    )


@router.get("/sessions/{session_id}/results", response_model=schemas.QuizResultsResponse)
def get_quiz_results(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    session = db.query(models.QuizSession).filter(
        and_(
            models.QuizSession.id == session_id,
            models.QuizSession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz session not found"
        )
    
    if not session.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz session not completed yet"
        )
    
    # Get answers with questions
    answers = db.query(models.Answer).filter(
        models.Answer.session_id == session_id
    ).all()
    
    # Get questions for correct answers
    question_ids = [a.question_id for a in answers]
    questions = {q.id: q for q in db.query(models.Question).filter(
        models.Question.id.in_(question_ids)
    ).all()}
    
    answer_responses = [
        schemas.AnswerResponse(
            id=a.id,
            question_id=a.question_id,
            user_answer=a.user_answer,
            is_correct=a.is_correct,
            submitted_at=a.submitted_at,
            correct_answer=questions.get(a.question_id).correct_answer if questions.get(a.question_id) else None
        )
        for a in answers
    ]
    
    # Get progress
    progress = db.query(models.UserProgress).filter(
        and_(
            models.UserProgress.user_id == current_user.id,
            models.UserProgress.topic_id == session.topic_id
        )
    ).first()
    
    topic_mastery = progress.mastery_percentage if progress else 0.0
    
    return schemas.QuizResultsResponse(
        session_id=session.id,
        score=session.score or 0.0,
        total_questions=len(answers),
        correct_answers=sum(1 for a in answers if a.is_correct),
        answers=answer_responses,
        topic_mastery=topic_mastery
    )
