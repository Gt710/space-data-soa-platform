from sqlalchemy import Column, Integer, String, Text, Date
from database import Base

class SpaceEvent(Base):
    __tablename__ = "space_events"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    title = Column(String(255))
    explanation = Column(Text)
    url = Column(String(500))
    media_type = Column(String(50))
