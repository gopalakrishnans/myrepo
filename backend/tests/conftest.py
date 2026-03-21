import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Hospital, Payer, Price, Procedure

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

    db = TestSession()
    h1 = Hospital(name="Test Hospital A", city="New York", state="NY", zip_code="10001")
    h2 = Hospital(name="Test Hospital B", city="Houston", state="TX", zip_code="77001")
    db.add_all([h1, h2])
    db.flush()

    p1 = Procedure(billing_code="70553", code_type="CPT",
                    description="MRI brain with contrast",
                    plain_language_name="Brain MRI with Contrast", category="Imaging")
    p2 = Procedure(billing_code="85025", code_type="CPT",
                    description="Complete blood count",
                    plain_language_name="Complete Blood Count (CBC)", category="Lab")
    db.add_all([p1, p2])
    db.flush()

    pay1 = Payer(name="Blue Cross", plan_name="PPO")
    db.add(pay1)
    db.flush()

    db.add_all([
        Price(hospital_id=h1.id, procedure_id=p1.id, payer_id=None,
              gross_charge=3000, discounted_cash_price=1500,
              min_negotiated_rate=800, max_negotiated_rate=1200),
        Price(hospital_id=h1.id, procedure_id=p1.id, payer_id=pay1.id,
              gross_charge=3000, discounted_cash_price=1500, negotiated_rate=1000,
              min_negotiated_rate=800, max_negotiated_rate=1200),
        Price(hospital_id=h2.id, procedure_id=p1.id, payer_id=None,
              gross_charge=2500, discounted_cash_price=1200,
              min_negotiated_rate=600, max_negotiated_rate=900),
        Price(hospital_id=h1.id, procedure_id=p2.id, payer_id=None,
              gross_charge=100, discounted_cash_price=50,
              min_negotiated_rate=20, max_negotiated_rate=40),
    ])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
