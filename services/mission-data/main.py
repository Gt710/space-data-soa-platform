from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
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

class MissionUpdate(BaseModel):
    name: Optional[str] = None
    agency: Optional[str] = None
    launch_date: Optional[date] = None
    status: Optional[str] = None
    description: Optional[str] = None

@app.get("/")
def read_root():
    return {"service": "mission-data", "status": "online"}

# === MISSIONS CRUD ===
@app.get("/missions/")
def get_missions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Mission).offset(skip).limit(limit).all()

@app.get("/missions/{mission_id}")
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    m = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Mission not found")
    return m

@app.post("/missions/")
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    db_mission = models.Mission(**mission.model_dump())
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    return db_mission

@app.put("/missions/{mission_id}")
def update_mission(mission_id: int, mission: MissionUpdate, db: Session = Depends(get_db)):
    db_m = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not db_m:
        raise HTTPException(status_code=404, detail="Mission not found")
    for key, value in mission.model_dump(exclude_unset=True).items():
        setattr(db_m, key, value)
    db.commit()
    db.refresh(db_m)
    return db_m

@app.delete("/missions/{mission_id}")
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    db_m = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not db_m:
        raise HTTPException(status_code=404, detail="Mission not found")
    db.delete(db_m)
    db.commit()
    return {"status": "deleted", "id": mission_id}

# === NASA APIs ===
@app.get("/apod/")
def get_apod():
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=f"NASA API error")

@app.get("/mars-photos/")
def get_mars_photos(sol: int = 1000, camera: str = "fhaz"):
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={sol}&camera={camera}&api_key={NASA_API_KEY}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="NASA API error")

@app.get("/neo/")
def get_near_earth_objects():
    """NASA Near-Earth Objects (asteroids) — today's feed"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            count = data.get("element_count", 0)
            neos = []
            for date_key, objects in data.get("near_earth_objects", {}).items():
                for obj in objects:
                    neos.append({
                        "id": obj.get("id"),
                        "name": obj.get("name"),
                        "estimated_diameter_m": {
                            "min": obj.get("estimated_diameter", {}).get("meters", {}).get("estimated_diameter_min", 0),
                            "max": obj.get("estimated_diameter", {}).get("meters", {}).get("estimated_diameter_max", 0)
                        },
                        "is_potentially_hazardous": obj.get("is_potentially_hazardous_asteroid", False),
                        "close_approach": obj.get("close_approach_data", [{}])[0].get("miss_distance", {}).get("astronomical", "—"),
                        "velocity_kmps": obj.get("close_approach_data", [{}])[0].get("relative_velocity", {}).get("kilometers_per_second", "—"),
                        "close_approach_date": obj.get("close_approach_data", [{}])[0].get("close_approach_date", "—")
                    })
            return {"status": "success", "count": count, "date": today, "data": neos}
        raise HTTPException(status_code=response.status_code, detail="NASA NEO API error")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
