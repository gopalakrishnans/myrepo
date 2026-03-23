from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    procedure_id = Column(Integer, ForeignKey("procedures.id"), nullable=False)
    payer_id = Column(Integer, ForeignKey("payers.id"), nullable=True)
    gross_charge = Column(Numeric(10, 2))
    discounted_cash_price = Column(Numeric(10, 2))
    negotiated_rate = Column(Numeric(10, 2))
    min_negotiated_rate = Column(Numeric(10, 2))
    max_negotiated_rate = Column(Numeric(10, 2))
    source_type = Column(String(20))  # "hospital_mrf" or "insurer_mrf" or "seed"
    source_file = Column(String(500))

    hospital = relationship("Hospital", back_populates="prices")
    procedure = relationship("Procedure", back_populates="prices")
    payer = relationship("Payer", back_populates="prices")

    __table_args__ = (
        Index("ix_price_procedure_hospital", "procedure_id", "hospital_id"),
    )
