from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Float,
    Boolean,
    JSON,
    ARRAY,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


# ======================
# User
# ======================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    quiz_sessions = relationship(
        "QuizSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    progress = relationship(
        "UserProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ======================
# Topic
# ======================

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    level = Column(String(10))  # A0, A1, A2, etc.

    prerequisite_topic_id = Column(
        Integer,
        ForeignKey("topics.id"),
        nullable=True
    )

    questions = relationship(
        "Question",
        back_populates="topic",
        cascade="all, delete-orphan"
    )
    quiz_sessions = relationship(
        "QuizSession",
        back_populates="topic"
    )
    progress = relationship(
        "UserProgress",
        back_populates="topic"
    )


# ======================
# Question
# ======================

class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    prompt = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)

    choices = Column(JSON)  # ["a", "b", "c"]
    correct_answer = Column(Text, nullable=False)

    explanation = Column(Text)
    hint = Column(Text)

    difficulty = Column(String(10), nullable=False, default="easy")
    tags = Column(ARRAY(String))  # ["past_tense", "irregular"]
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)

    topic = relationship("Topic", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


# ======================
# Quiz Session
# ======================

class QuizMode(str, enum.Enum):
    NORMAL = "normal"
    HARD = "hard"
    TIMED = "timed"


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    mode = Column(
        String(20),
        nullable=False,
        default=QuizMode.NORMAL.value
    )

    started_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)  # percentage

    user = relationship("User", back_populates="quiz_sessions")
    topic = relationship("Topic", back_populates="quiz_sessions")
    answers = relationship(
        "Answer",
        back_populates="session",
        cascade="all, delete-orphan"
    )


# ======================
# Answer
# ======================

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    submitted_at = Column(DateTime, default=func.now(), nullable=False)

    session = relationship("QuizSession", back_populates="answers")
    question = relationship("Question", back_populates="answers")


# ======================
# User Progress
# ======================

class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "topic_id",
            name="uq_user_topic_progress"
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    mastery_percentage = Column(Float, default=0.0, nullable=False)
    questions_answered = Column(Integer, default=0, nullable=False)

    last_updated = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user = relationship("User", back_populates="progress")
    topic = relationship("Topic", back_populates="progress")
