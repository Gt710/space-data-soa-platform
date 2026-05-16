from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import requests
import os
from dotenv import load_dotenv

# Імпорти наших модулів
from database import engine, get_db, Base
import models

# Створюємо таблиці, якщо їх немає
Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI(title="Space Weather Service")

NASA_API_KEY = os.getenv("NASA_API_KEY")

@app.get("/")
def read_root():
    return {"message": "Hello World from Space Weather Service", "status": "active"}

@app.get("/nasa-test")
def test_nasa_api(db: Session = Depends(get_db)):
    if not NASA_API_KEY:
        raise HTTPException(status_code=500, detail="NASA_API_KEY not found in .env")
    
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Зберігаємо в базу даних
        new_event = models.SpaceEvent(
            date=data.get("date"),
            title=data.get("title"),
            explanation=data.get("explanation"),
            url=data.get("url"),
            media_type=data.get("media_type")
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        return {"status": "Saved to DB", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/events")
def get_events(db: Session = Depends(get_db)):
    return db.query(models.SpaceEvent).all()
