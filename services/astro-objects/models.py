from sqlalchemy import Column, Integer, String, Float
from database import Base

class AstroObject(Base):
    __tablename__ = "astro_objects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    object_type = Column(String(100)) # Star, Galaxy, Nebula
    right_ascension = Column(String(100))
    declination = Column(String(100))
    distance_ly = Column(Float, nullable=True) # Distance in light years
