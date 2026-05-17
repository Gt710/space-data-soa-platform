from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx, logging

from auth import require_auth
from database import engine, get_db, Base
import models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("satellite-tracker")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Satellite Tracker Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"service": "satellite-tracker", "status": "online"}


@app.get("/satellites")
def get_satellites(db: Session = Depends(get_db)):
    sats = db.query(models.Satellite).all()
    return [
        {"name": s.name, "norad_id": s.norad_id, "launch_date": s.launch_date,
         "tle_line1": s.tle_line1 or "", "tle_line2": s.tle_line2 or ""}
        for s in sats
    ]


@app.get("/satellites/{norad_id}")
def get_satellite_by_norad(norad_id: int, db: Session = Depends(get_db)):
    sat = db.query(models.Satellite).filter(models.Satellite.norad_id == norad_id).first()
    if not sat:
        raise HTTPException(status_code=404, detail="Satellite not found")
    return {"name": sat.name, "norad_id": sat.norad_id, "launch_date": sat.launch_date,
            "tle_line1": sat.tle_line1 or "", "tle_line2": sat.tle_line2 or ""}


@app.get("/add-test")
def add_test_satellite(db: Session = Depends(get_db)):
    existing = db.query(models.Satellite).filter(models.Satellite.norad_id == 25544).first()
    if not existing:
        sat = models.Satellite(name="ISS (ZARYA)", norad_id=25544, launch_date="1998-11-20")
        db.add(sat)
        db.commit()
    return {"status": "Added ISS to DB"}


class SatelliteCreate(BaseModel):
    name: str
    norad_id: int
    launch_date: str | None = None
    tle_line1: str | None = None
    tle_line2: str | None = None


@app.post("/satellites")
def create_satellite(sat: SatelliteCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Satellite).filter(models.Satellite.norad_id == sat.norad_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Satellite with this NORAD ID already exists")
    db_sat = models.Satellite(**sat.model_dump())
    db.add(db_sat)
    db.commit()
    db.refresh(db_sat)
    return db_sat


@app.get("/fetch-tle")
async def fetch_tle(db: Session = Depends(get_db)):
    """Fetch TLE from Celestrak, fallback to database if unavailable"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
            )
            tle_data = response.text

        lines = [line for line in tle_data.splitlines() if line.strip()]
        parsed = []

        for i in range(0, min(len(lines), 30), 3):
            if i + 2 < len(lines):
                name = lines[i].strip()
                line1 = lines[i + 1]
                line2 = lines[i + 2]

                if not line1.startswith("1 ") or not line2.startswith("2 "):
                    continue

                norad_id = line1[2:7].strip()
                parsed.append({
                    "name": name,
                    "norad_id": norad_id,
                    "tle_line1": line1,
                    "tle_line2": line2
                })

        if parsed:
            logger.info(f"Celestrak: fetched {len(parsed)} satellites")
            return {"status": "success", "source": "celestrak", "count": len(parsed), "data": parsed}
    except Exception as e:
        logger.warning(f"Celestrak unavailable: {e}")

    # Fallback to database
    sats = db.query(models.Satellite).filter(models.Satellite.tle_line1.isnot(None)).all()
    db_data = [
        {"name": s.name, "norad_id": str(s.norad_id), "tle_line1": s.tle_line1, "tle_line2": s.tle_line2}
        for s in sats
    ]
    logger.info(f"Fallback to DB: {len(db_data)} satellites")
    return {"status": "success", "source": "database", "count": len(db_data), "data": db_data}


@app.post("/save-tle")
async def save_tle_to_db(db: Session = Depends(get_db)):
    """Fetch TLE and save satellites to database"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
            )
        lines = [line for line in response.text.splitlines() if line.strip()]
        saved = 0
        for i in range(0, min(len(lines), 60), 3):
            if i + 2 < len(lines):
                name = lines[i].strip()
                line1 = lines[i + 1]
                line2 = lines[i + 2]
                if not line1.startswith("1 ") or not line2.startswith("2 "):
                    continue
                norad_id = int(line1[2:7].strip())
                existing = db.query(models.Satellite).filter(models.Satellite.norad_id == norad_id).first()
                if not existing:
                    db.add(models.Satellite(name=name, norad_id=norad_id, launch_date=None,
                                           tle_line1=line1, tle_line2=line2))
                    saved += 1
        db.commit()
        return {"status": "success", "saved": saved}
    except Exception as e:
        return {"status": "error", "message": str(e)}
