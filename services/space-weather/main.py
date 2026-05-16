from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
import os
from dotenv import load_dotenv

from database import engine, get_db, Base
import models

Base.metadata.create_all(bind=engine)
load_dotenv()

app = FastAPI(title="Space Weather Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

@app.get("/")
def read_root():
    return {"message": "Space Weather Service", "status": "active"}

@app.get("/noaa-kp-index")
def get_noaa_kp_index():
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if len(data) > 1:
            headers = data[0]
            latest_entry = data[-1]
            # Build proper dict from headers + values
            header_keys = headers if isinstance(headers, list) else list(headers)
            latest_dict = {}
            if isinstance(latest_entry, list):
                for i, key in enumerate(header_keys):
                    if i < len(latest_entry):
                        val = latest_entry[i]
                        try:
                            val = float(val)
                        except (ValueError, TypeError):
                            pass
                        latest_dict[key] = val
            else:
                latest_dict = latest_entry
            return {
                "status": "success",
                "source": "NOAA SWPC",
                "headers": latest_dict,
                "latest_kp_index": latest_dict
            }
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NOAA API Error: {str(e)}")

@app.get("/kp-history")
def get_kp_history():
    """Returns last 7 days of Kp index data for charts"""
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if len(data) > 1:
            headers = data[0]
            entries = []
            for entry in data[-56:]:  # Last ~7 days (8 measurements/day)
                if isinstance(entry, list) and len(entry) >= 2:
                    entries.append({"time_tag": entry[0], "Kp": float(entry[1]) if entry[1] else 0})
            return {"status": "success", "count": len(entries), "data": entries}
        return {"status": "success", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/donki/cme")
def get_coronal_mass_ejections():
    """NASA DONKI - Coronal Mass Ejections (last 30 days)"""
    url = f"https://api.nasa.gov/DONKI/CME?api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            events = []
            for event in data[:10]:
                events.append({
                    "id": event.get("activityID"),
                    "startTime": event.get("startTime"),
                    "sourceLocation": event.get("sourceLocation"),
                    "note": (event.get("note") or "")[:200],
                    "instruments": [i.get("displayName") for i in event.get("instruments", [])]
                })
            return {"status": "success", "count": len(events), "data": events}
        raise HTTPException(status_code=response.status_code, detail="DONKI CME API error")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/donki/flr")
def get_solar_flares():
    """NASA DONKI - Solar Flares (last 30 days)"""
    url = f"https://api.nasa.gov/DONKI/FLR?api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            flares = []
            for flare in data[:10]:
                flares.append({
                    "id": flare.get("flrID"),
                    "beginTime": flare.get("beginTime"),
                    "peakTime": flare.get("peakTime"),
                    "endTime": flare.get("endTime"),
                    "classType": flare.get("classType"),
                    "sourceLocation": flare.get("sourceLocation")
                })
            return {"status": "success", "count": len(flares), "data": flares}
        raise HTTPException(status_code=response.status_code, detail="DONKI FLR API error")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/donki/gst")
def get_geomagnetic_storms():
    """NASA DONKI - Geomagnetic Storms (last 30 days)"""
    url = f"https://api.nasa.gov/DONKI/GST?api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            storms = []
            for storm in data[:10]:
                kp_values = []
                for idx in storm.get("allKpIndex", []):
                    kp_values.append({"observedTime": idx.get("observedTime"), "kpIndex": idx.get("kpIndex")})
                storms.append({
                    "id": storm.get("gstID"),
                    "startTime": storm.get("startTime"),
                    "kpIndex": kp_values
                })
            return {"status": "success", "count": len(storms), "data": storms}
        raise HTTPException(status_code=response.status_code, detail="DONKI GST API error")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nasa-test")
def test_nasa_api(db: Session = Depends(get_db)):
    if not NASA_API_KEY:
        raise HTTPException(status_code=500, detail="NASA_API_KEY not found")
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        new_event = models.SpaceEvent(
            date=data.get("date"), title=data.get("title"),
            explanation=data.get("explanation"), url=data.get("url"),
            media_type=data.get("media_type")
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return {"status": "Saved to DB", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events")
def get_events(db: Session = Depends(get_db)):
    return db.query(models.SpaceEvent).all()
