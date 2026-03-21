from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Payer(Base):
    __tablename__ = "payers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    plan_name = Column(String(255))

    prices = relationship("Price", back_populates="payer")
