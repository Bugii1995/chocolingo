from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import enum
from pydantic import field_validator
from app.models import QuestionType

# ======================
# API Enums (API-only)
# ======================

class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"


class QuizMode(str, enum.Enum):
    NORMAL = "normal"
    HARD = "hard"
    TIMED = "timed"


# ======================
# Auth Schemas
# ======================

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ======================
# Topic Schemas
# ======================

class TopicResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    level: Optional[str]
    prerequisite_topic_id: Optional[int]
    question_count: Optional[int] = None

    class Config:
        from_attributes = True


class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    level: Optional[str] = None
    prerequisite_topic_id: Optional[int] = None


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    prerequisite_topic_id: Optional[int] = None


class TopicAdminResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    level: Optional[str]
    prerequisite_topic_id: Optional[int]
    question_count: int

    class Config:
        from_attributes = True


# ======================
# Question Schemas
# ======================

# Public / Quiz-safe
class QuestionResponse(BaseModel):
    id: int
    topic_id: int
    prompt: str
    question_type: QuestionType
    choices: Optional[List[str]]

    class Config:
        from_attributes = True


# Admin / Internal
class QuestionAdminResponse(BaseModel):
    id: int
    topic_id: int
    prompt: str
    question_type: QuestionType
    choices: list[str] | None
    correct_answer: str
    explanation: str | None
    hint: str | None
    difficulty: str
    tags: list[str] | None
    is_active: bool
    created_at: datetime

    @field_validator("question_type", mode="before")
    @classmethod
    def normalize_question_type(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    class Config:
        from_attributes = True



class QuestionCreate(BaseModel):
    topic_id: int
    prompt: str
    question_type: QuestionType
    choices: Optional[List[str]]
    correct_answer: str
    explanation: Optional[str]
    hint: Optional[str]
    difficulty: str = "easy"
    tags: Optional[List[str]]
    is_active: bool = True


class QuestionUpdate(BaseModel):
    prompt: Optional[str]
    question_type: Optional[QuestionType]
    choices: Optional[List[str]]
    correct_answer: Optional[str]
    explanation: Optional[str]
    hint: Optional[str]
    difficulty: Optional[str]
    tags: Optional[List[str]]
    is_active: Optional[bool]


class PaginatedQuestionsResponse(BaseModel):
    items: List[QuestionAdminResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ======================
# Quiz Schemas
# ======================

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
    answer: str


class AnswersSubmit(BaseModel):
    answers: List[AnswerSubmit]


class AnswerResponse(BaseModel):
    id: int
    question_id: int
    user_answer: str
    is_correct: bool
    submitted_at: datetime
    correct_answer: Optional[str] = None

    class Config:
        from_attributes = True


class QuizResultsResponse(BaseModel):
    session_id: int
    score: float
    total_questions: int
    correct_answers: int
    answers: List[AnswerResponse]
    topic_mastery: float


# ======================
# Progress / Dashboard
# ======================

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


# ======================
# Progress Map (UI-driven)
# ======================

class MapNode(BaseModel):
    id: int
    title: str
    status: str  # locked | active | completed
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


# ======================
# Admin Dashboard Schemas
# ======================

class AdminDashboardStats(BaseModel):
    total_topics: int
    total_questions: int
    active_questions: int
    inactive_questions: int
    total_users: int
