from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Procedure(Base):
    __tablename__ = "procedures"

    id = Column(Integer, primary_key=True, index=True)
    billing_code = Column(String(20), nullable=False)
    code_type = Column(String(10), nullable=False)
    description = Column(String(500))
    plain_language_name = Column(String(255), nullable=False)
    category = Column(String(100))

    prices = relationship("Price", back_populates="procedure")
