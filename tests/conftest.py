import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from main import app

# In-memory SQLite database for deterministic test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    # Seed exercises
    from app.data.exercises_gym import FULL_GYM_EXERCISES
    from app.data.exercises_dumbbells import DUMBBELL_EXERCISES
    from app.data.exercises_bodyweight import BODYWEIGHT_EXERCISES
    from app.models.exercise import Exercise

    db = TestingSessionLocal()
    for item in FULL_GYM_EXERCISES + DUMBBELL_EXERCISES + BODYWEIGHT_EXERCISES:
        ex = Exercise(
            name=item["name"],
            primary_muscle=item["primary_muscle"],
            secondary_muscles=item.get("secondary_muscles", ""),
            movement_pattern=item["movement_pattern"],
            equipment_tier=item["equipment_tier"],
            target_goals=item["target_goals"],
            spinal_compression=item.get("spinal_compression", "none"),
            knee_stress=item.get("knee_stress", "none"),
            shoulder_stress=item.get("shoulder_stress", "none"),
            wrist_stress=item.get("wrist_stress", "none"),
            gender_focus=item.get("gender_focus", "unisex"),
            contraindicated_injuries=item.get("contraindicated_injuries", ""),
            is_bodyweight=item.get("is_bodyweight", False),
            instructions=item.get("instructions", "")
        )
        db.add(ex)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
