from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import QuestionType, QuizMode


# Auth schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# Topic schemas
class TopicResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    level: Optional[str]
    prerequisite_topic_id: Optional[int]

    class Config:
        from_attributes = True


# Question schemas
class QuestionResponse(BaseModel):
    id: int
    topic_id: int
    prompt: str
    question_type: QuestionType
    choices: Optional[List[str]]
    # Note: correct_answer is NOT included for security

    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionResponse):
    correct_answer: str
    explanation: Optional[str]


# Quiz schemas
class QuizSessionCreate(BaseModel):
    topic_id: int
    mode: QuizMode = QuizMode.NORMAL


class QuizSessionResponse(BaseModel):
    id: int
    user_id: int
    topic_id: int
    mode: QuizMode
    started_at: datetime
    completed_at: Optional[datetime]
    score: Optional[float]
    questions: List[QuestionResponse]

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    question_id: int
    user_answer: str


class AnswersSubmit(BaseModel):
    answers: List[AnswerSubmit]


class AnswerResponse(BaseModel):
    id: int
    question_id: int
    user_answer: str
    is_correct: bool
    submitted_at: datetime
    correct_answer: Optional[str] = None  # Only included in results

    class Config:
        from_attributes = True


class QuizResultsResponse(BaseModel):
    session_id: int
    score: float
    total_questions: int
    correct_answers: int
    answers: List[AnswerResponse]
    topic_mastery: float


# Progress schemas
class DashboardStats(BaseModel):
    streak: int
    today_completed: int
    today_goal: int
    total_answered: int
    accuracy: float


class TopicProgress(BaseModel):
    topic_id: int
    mastery_percentage: float
    questions_answered: int
    last_updated: datetime

    class Config:
        from_attributes = True


class MapNode(BaseModel):
    id: int
    title: str
    status: str  # 'locked', 'active', 'completed'
    mastery: float


class MapLevel(BaseModel):
    level: str
    nodes: List[MapNode]
    mastery: float


class MapCluster(BaseModel):
    id: int
    title: str
    levels: List[MapLevel]


class MapResponse(BaseModel):
    clusters: List[MapCluster]
