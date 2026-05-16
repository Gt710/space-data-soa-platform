from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
import os
from datetime import date

from database import engine, get_db, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mission Data Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from dotenv import load_dotenv
load_dotenv()
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")


class MissionCreate(BaseModel):
    name: str
    agency: str
    launch_date: date | None = None
    status: str
    description: str | None = None

@app.get("/")
def read_root():
    return {"service": "mission-data", "status": "online"}

@app.get("/mars-photos/")
def get_mars_photos(sol: int = 1000, camera: str = "fhaz"):
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={sol}&camera={camera}&api_key={NASA_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=f"NASA API error: {response.text}")

@app.get("/apod/")
def get_apod():
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=f"NASA API error: {response.text}")

@app.post("/missions/")
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    db_mission = models.Mission(**mission.model_dump())
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    return db_mission

@app.get("/missions/")
def get_missions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Mission).offset(skip).limit(limit).all()
