"""
Seed script to populate database with sample data for testing.
Run with: python seed_data.py
"""
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash

# Create tables
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Create a test user
    test_user = db.query(models.User).filter(models.User.username == "testuser").first()
    if not test_user:
        test_user = models.User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("testpass123")
        )
        db.add(test_user)
        db.commit()
        print("Created test user: testuser / testpass123")
    else:
        print("Test user already exists")

    # Create topics
    topic1 = db.query(models.Topic).filter(models.Topic.title == "Basic Verbs").first()
    if not topic1:
        topic1 = models.Topic(
            title="Basic Verbs",
            description="Learn the most common verbs",
            level="A0"
        )
        db.add(topic1)
        db.flush()

        # Add questions for topic1
        questions1 = [
            models.Question(
                topic_id=topic1.id,
                prompt="What is the past tense of 'go'?",
                question_type=models.QuestionType.MULTIPLE_CHOICE,
                choices=["went", "goed", "goes", "going"],
                correct_answer="went",
                explanation="The past tense of 'go' is 'went'."
            ),
            models.Question(
                topic_id=topic1.id,
                prompt="Complete: I ___ to the store yesterday.",
                question_type=models.QuestionType.FILL_BLANK,
                choices=None,
                correct_answer="went",
                explanation="Use 'went' for past tense actions."
            ),
            models.Question(
                topic_id=topic1.id,
                prompt="What is the present tense of 'ran'?",
                question_type=models.QuestionType.MULTIPLE_CHOICE,
                choices=["run", "runs", "running", "runned"],
                correct_answer="run",
                explanation="'Run' is the present tense form."
            ),
        ]
        db.add_all(questions1)
        print(f"Created topic: {topic1.title} with {len(questions1)} questions")

    topic2 = db.query(models.Topic).filter(models.Topic.title == "Pronouns").first()
    if not topic2:
        topic2 = models.Topic(
            title="Pronouns",
            description="Learn about personal pronouns",
            level="A0"
        )
        db.add(topic2)
        db.flush()

        questions2 = [
            models.Question(
                topic_id=topic2.id,
                prompt="Which pronoun is used for 'he' or 'she'?",
                question_type=models.QuestionType.MULTIPLE_CHOICE,
                choices=["they", "it", "we", "you"],
                correct_answer="they",
                explanation="'They' can refer to he or she in modern English."
            ),
            models.Question(
                topic_id=topic2.id,
                prompt="Complete: ___ are learning English.",
                question_type=models.QuestionType.FILL_BLANK,
                choices=None,
                correct_answer="We",
                explanation="'We' is the first person plural pronoun."
            ),
        ]
        db.add_all(questions2)
        print(f"Created topic: {topic2.title} with {len(questions2)} questions")

    db.commit()
    print("\nSeed data created successfully!")
    print("\nYou can now:")
    print("1. Register a new user at /auth/register")
    print("2. Or login with testuser / testpass123")

except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
