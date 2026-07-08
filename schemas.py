from datetime import date
from typing import Optional
from pydantic import BaseModel

class PlaceIn(BaseModel):
    external_id: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: Optional[list[PlaceIn]] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None

class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    visited: Optional[bool] = None

class PlaceOut(BaseModel):
    id: int
    external_id: str
    title: str
    notes: Optional[str]
    visited: bool
    class Config:
        from_attributes = True

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    completed: bool
    places: list[PlaceOut] = []
    class Config:
        from_attributes = True