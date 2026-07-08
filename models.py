from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class ProjectPlace(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="travelproject.id")
    external_id: str
    title: str
    notes: Optional[str] = None
    visited: bool = False

    project: Optional["TravelProject"] = Relationship(back_populates="places")

class TravelProject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    completed: bool = False

    places: list[ProjectPlace] = Relationship(back_populates="project")