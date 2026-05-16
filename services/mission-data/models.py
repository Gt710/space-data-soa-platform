from sqlalchemy import Column, Integer, String, Date, Text
from database import Base

class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    agency = Column(String(100)) # NASA, ESA, SpaceX
    launch_date = Column(Date, nullable=True)
    status = Column(String(50)) # Active, Completed, Planned
    description = Column(Text, nullable=True)
