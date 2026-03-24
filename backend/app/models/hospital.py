from sqlalchemy import Boolean, Column, Date, Float, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    ein = Column(String(20))
    npi = Column(String(10), index=True)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    last_updated = Column(Date)

    # Contact
    phone = Column(String(20))
    website = Column(String(500))
    booking_url = Column(String(500))

    # Facility classification
    facility_type = Column(String(50))  # "hospital", "imaging_center", "clinic"

    # Mammography-specific
    has_3d_mammography = Column(Boolean)
    acr_accredited = Column(Boolean)
    accepts_new_patients = Column(Boolean)
    availability_note = Column(String(255))  # e.g. "Typically books within 2 weeks"
    accepted_insurances = Column(JSON)  # list of insurance name strings

    prices = relationship("Price", back_populates="hospital")
