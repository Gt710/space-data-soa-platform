from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
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

class AstroObjectUpdate(BaseModel):
    name: Optional[str] = None
    object_type: Optional[str] = None
    right_ascension: Optional[str] = None
    declination: Optional[str] = None
    distance_ly: Optional[float] = None

@app.get("/")
def read_root():
    return {"service": "astro-objects", "status": "online"}

@app.get("/objects/")
def get_objects(skip: int = 0, limit: int = 100, object_type: str = None, db: Session = Depends(get_db)):
    query = db.query(models.AstroObject)
    if object_type:
        query = query.filter(models.AstroObject.object_type == object_type)
    return query.offset(skip).limit(limit).all()

@app.get("/objects/{obj_id}")
def get_object(obj_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.AstroObject).filter(models.AstroObject.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

@app.post("/objects/")
def create_object(obj: AstroObjectCreate, db: Session = Depends(get_db)):
    db_obj = models.AstroObject(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.put("/objects/{obj_id}")
def update_object(obj_id: int, obj: AstroObjectUpdate, db: Session = Depends(get_db)):
    db_obj = db.query(models.AstroObject).filter(models.AstroObject.id == obj_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Object not found")
    for key, value in obj.model_dump(exclude_unset=True).items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@app.delete("/objects/{obj_id}")
def delete_object(obj_id: int, db: Session = Depends(get_db)):
    db_obj = db.query(models.AstroObject).filter(models.AstroObject.id == obj_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Object not found")
    db.delete(db_obj)
    db.commit()
    return {"status": "deleted", "id": obj_id}

@app.get("/search/{name}")
def search_external(name: str):
    """Search object in Simbad via TAP"""
    try:
        url = "https://simbad.cds.unistra.fr/simbad/sim-basic"
        params = {"Ident": name, "submit": "SIMBAD search", "output.format": "ASCII"}
        response = requests.get(url, params=params, timeout=10)
        return {
            "query": name,
            "source": "Simbad CDS",
            "status": "found" if response.status_code == 200 else "not_found",
            "raw_data": response.text[:500] if response.status_code == 200 else None
        }
    except Exception as e:
        return {"query": name, "status": "error", "message": str(e)}

@app.get("/object-types")
def get_object_types(db: Session = Depends(get_db)):
    types = db.query(models.AstroObject.object_type).distinct().all()
    return [t[0] for t in types if t[0]]
