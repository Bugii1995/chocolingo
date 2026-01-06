from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)

    questions = relationship(
        "Question",
        back_populates="topic",
        cascade="all, delete-orphan"
    )

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)

    topic = relationship("Topic", back_populates="questions")
