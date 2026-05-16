from sqlalchemy import Column, Integer, String
from database import Base

class Satellite(Base):
    __tablename__ = "satellites"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    norad_id = Column(Integer, unique=True, nullable=False)
    launch_date = Column(String(20), nullable=True)
