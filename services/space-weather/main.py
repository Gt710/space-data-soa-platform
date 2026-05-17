from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests, os, logging
from dotenv import load_dotenv

from database import engine, get_db, Base
import models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("space-weather")

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

import random

def parse_noaa_kp_data(data):
    if not data:
        return []
    entries = []
    if isinstance(data[0], list):
        headers = data[0]
        time_idx = headers.index("time_tag") if "time_tag" in headers else 0
        kp_idx = headers.index("Kp") if "Kp" in headers else 1
        for row in data[1:]:
            if isinstance(row, list) and len(row) > max(time_idx, kp_idx):
                try:
                    kp_val = float(row[kp_idx]) if row[kp_idx] else 0.0
                except (ValueError, TypeError):
                    kp_val = 0.0
                entries.append({"time_tag": row[time_idx], "Kp": kp_val})
    else:
        for item in data:
            if isinstance(item, dict):
                kp_val = item.get("Kp")
                if kp_val is None:
                    kp_val = item.get("kp")
                if kp_val is None:
                    kp_val = 0.0
                try:
                    kp_val = float(kp_val)
                except (ValueError, TypeError):
                    kp_val = 0.0
                entries.append({
                    "time_tag": item.get("time_tag") or item.get("time") or "",
                    "Kp": kp_val
                })
    return entries

@app.get("/noaa-kp-index")
def get_noaa_kp_index():
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        parsed = parse_noaa_kp_data(data)
        if parsed:
            latest = parsed[-1]
            return {
                "status": "success",
                "source": "NOAA SWPC",
                "headers": latest,
                "latest_kp_index": latest
            }
    except Exception as e:
        logger.warning(f"NOAA Kp Index fetch failed: {e}")
    
    # Fallback to realistic Kp index
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    latest_dict = {"time_tag": now_str, "Kp": 2.33}
    return {
        "status": "fallback",
        "source": "NOAA SWPC (Fallback)",
        "headers": latest_dict,
        "latest_kp_index": latest_dict
    }

@app.get("/kp-history")
def get_kp_history():
    """Returns last 7 days of Kp index data for charts"""
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        parsed = parse_noaa_kp_data(data)
        if parsed:
            return {"status": "success", "count": len(parsed[-56:]), "data": parsed[-56:]}
    except Exception as e:
        logger.warning(f"NOAA Kp History fetch failed: {e}")
    
    # Generate realistic historical dataset of 56 entries
    now = datetime.now()
    entries = []
    for i in range(56, 0, -1):
        t = now - timedelta(hours=i*3)
        dist_from_peak = abs(28 - (56 - i))
        base_kp = 1.0 + random.uniform(0.2, 1.5)
        if dist_from_peak < 10:
            base_kp += (10 - dist_from_peak) * 0.5
        entries.append({
            "time_tag": t.strftime("%Y-%m-%dT%H:%M:%S"),
            "Kp": round(min(base_kp, 9.0), 2)
        })
    return {"status": "fallback", "count": len(entries), "data": entries}

from datetime import datetime, timedelta

def _fallback_dates():
    now = datetime.now()
    return [(now - timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%SZ") for i in range(14)]

FALLBACK_CME = [
    {"id": "2026-05-14T06:12:00-CME-001", "startTime": None, "sourceLocation": "S15W30", "note": "Full halo CME observed. Speed ~890 km/s. Estimated Earth arrival in 2-3 days.", "instruments": ["LASCO C2", "LASCO C3"]},
    {"id": "2026-05-11T14:36:00-CME-001", "startTime": None, "sourceLocation": "N20E45", "note": "Partial halo CME. Speed ~620 km/s. Not Earth-directed.", "instruments": ["LASCO C2"]},
    {"id": "2026-05-08T09:48:00-CME-001", "startTime": None, "sourceLocation": "S25W60", "note": "Narrow CME associated with M2.1 flare. Speed ~540 km/s.", "instruments": ["LASCO C2", "STEREO-A COR2"]},
]

FALLBACK_FLR = [
    {"id": "FLR-2026-05-15", "beginTime": None, "peakTime": None, "endTime": None, "classType": "X1.8", "sourceLocation": "S15W30"},
    {"id": "FLR-2026-05-12", "beginTime": None, "peakTime": None, "endTime": None, "classType": "M5.2", "sourceLocation": "N20E10"},
    {"id": "FLR-2026-05-10", "beginTime": None, "peakTime": None, "endTime": None, "classType": "M2.1", "sourceLocation": "S25W60"},
    {"id": "FLR-2026-05-07", "beginTime": None, "peakTime": None, "endTime": None, "classType": "C9.4", "sourceLocation": "N15W20"},
    {"id": "FLR-2026-05-05", "beginTime": None, "peakTime": None, "endTime": None, "classType": "X3.1", "sourceLocation": "S10E35"},
]

FALLBACK_GST = [
    {"id": "GST-2026-05-16", "startTime": None, "kpIndex": [{"observedTime": None, "kpIndex": 6}, {"observedTime": None, "kpIndex": 7}]},
    {"id": "GST-2026-05-11", "startTime": None, "kpIndex": [{"observedTime": None, "kpIndex": 5}]},
]

def _fill_fallback_dates(items, key_map):
    dates = _fallback_dates()
    for i, item in enumerate(items):
        for key, offset in key_map.items():
            if item.get(key) is None:
                item[key] = dates[min(i * 2 + offset, len(dates) - 1)]
    return items

@app.get("/donki/cme")
def get_coronal_mass_ejections():
    """NASA DONKI - Coronal Mass Ejections (last 30 days)"""
    url = f"https://api.nasa.gov/DONKI/CME?api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=30)
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
        logger.warning(f"DONKI CME returned {response.status_code}")
    except Exception as e:
        logger.error(f"DONKI CME error: {e}")
    fallback = _fill_fallback_dates([dict(c) for c in FALLBACK_CME], {"startTime": 0})
    return {"status": "fallback", "count": len(fallback), "data": fallback}

@app.get("/donki/flr")
def get_solar_flares():
    """NASA DONKI - Solar Flares (last 30 days)"""
    url = f"https://api.nasa.gov/DONKI/FLR?api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=30)
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
        logger.warning(f"DONKI FLR returned {response.status_code}")
    except Exception as e:
        logger.error(f"DONKI FLR error: {e}")
    fallback = _fill_fallback_dates([dict(f) for f in FALLBACK_FLR], {"beginTime": 0, "peakTime": 0, "endTime": 1})
    return {"status": "fallback", "count": len(fallback), "data": fallback}

@app.get("/donki/gst")
def get_geomagnetic_storms():
    """NASA DONKI - Geomagnetic Storms (last 30 days)"""
    url = f"https://api.nasa.gov/DONKI/GST?api_key={NASA_API_KEY}"
    try:
        response = requests.get(url, timeout=30)
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
        logger.warning(f"DONKI GST returned {response.status_code}")
    except Exception as e:
        logger.error(f"DONKI GST error: {e}")
    fallback = _fill_fallback_dates([dict(g) for g in FALLBACK_GST], {"startTime": 0})
    for g in fallback:
        for kp in g.get("kpIndex", []):
            if kp.get("observedTime") is None:
                kp["observedTime"] = g["startTime"]
    return {"status": "fallback", "count": len(fallback), "data": fallback}

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
