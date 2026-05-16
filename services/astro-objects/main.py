from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests

from database import engine, get_db, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Astro Objects Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AstroObjectCreate(BaseModel):
    name: str
    object_type: str
    right_ascension: str
    declination: str
    distance_ly: float | None = None

@app.get("/")
def read_root():
    return {"service": "astro-objects", "status": "online"}

@app.post("/objects/")
def create_object(obj: AstroObjectCreate, db: Session = Depends(get_db)):
    db_obj = models.AstroObject(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.get("/objects/")
def get_objects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.AstroObject).offset(skip).limit(limit).all()

# Інтеграція з відкритим API (наприклад, для отримання базової інформації)
# В реальному дипломі тут може бути Simbad TAP API
@app.get("/search/{name}")
def search_external(name: str):
    # Симуляція пошуку
    return {"message": f"Пошук об'єкта {name} у зовнішніх каталогах...", "status": "Not completely implemented yet"}
