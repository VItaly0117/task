from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import Session, select
from typing import List

from database import init_db, get_session
from models import TravelProject, ProjectPlace
from schemas import ProjectCreate, ProjectUpdate, PlaceIn, PlaceUpdate, ProjectOut, PlaceOut
from external_api import fetch_artwork

app = FastAPI(title="Travel Planner API")


@app.on_event("startup")
def on_startup():
    # создаём таблицы в базе данных при запуске приложения
    init_db()


async def add_place_to_project(project_id: int, place_in: PlaceIn, session: Session) -> ProjectPlace:
    """
    Общая функция для двух случаев: (1) создание проекта сразу с местами,
    (2) добавление одного места в уже существующий проект.
    Делает две проверки перед сохранением:
    1. Это место ещё не добавлено в этот проект?
    2. Это место реально существует во внешнем API?
    """
    already_added = session.exec(
        select(ProjectPlace).where(
            ProjectPlace.project_id == project_id,
            ProjectPlace.external_id == place_in.external_id,
        )
    ).first()

    if already_added:
        raise HTTPException(status_code=400, detail="This place is already in the project")

    artwork = await fetch_artwork(place_in.external_id)
    if artwork is None:
        raise HTTPException(status_code=400, detail="This place was not found in the Art Institute API")

    return ProjectPlace(
        project_id=project_id,
        external_id=artwork["id"],
        title=artwork["title"],
    )


# ---------- Projects ----------

@app.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, session: Session = Depends(get_session)):
    if payload.places and len(payload.places) > 10:
        raise HTTPException(status_code=400, detail="A project can have at most 10 places")

    project = TravelProject(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )
    session.add(project)
    session.commit()
    session.refresh(project)  # чтобы получить project.id из базы

    if payload.places:
        for place_in in payload.places:
            new_place = await add_place_to_project(project.id, place_in, session)
            session.add(new_place)
        session.commit()
        session.refresh(project)

    return project


@app.get("/projects", response_model=List[ProjectOut])
def list_projects(session: Session = Depends(get_session)):
    return session.exec(select(TravelProject)).all()


@app.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, session: Session = Depends(get_session)):
    project = session.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(project, field_name, value)

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    has_visited_place = any(place.visited for place in project.places)
    if has_visited_place:
        raise HTTPException(status_code=400, detail="Cannot delete a project with visited places")

    session.delete(project)
    session.commit()


# ---------- Places ----------

@app.post("/projects/{project_id}/places", response_model=PlaceOut, status_code=status.HTTP_201_CREATED)
async def add_place(project_id: int, payload: PlaceIn, session: Session = Depends(get_session)):
    project = session.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(project.places) >= 10:
        raise HTTPException(status_code=400, detail="Project already has 10 places")

    new_place = await add_place_to_project(project_id, payload, session)
    session.add(new_place)
    session.commit()
    session.refresh(new_place)
    return new_place


@app.get("/projects/{project_id}/places", response_model=List[PlaceOut])
def list_places(project_id: int, session: Session = Depends(get_session)):
    project = session.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.places


@app.get("/projects/{project_id}/places/{place_id}", response_model=PlaceOut)
def get_place(project_id: int, place_id: int, session: Session = Depends(get_session)):
    place = session.get(ProjectPlace, place_id)
    if not place or place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@app.patch("/projects/{project_id}/places/{place_id}", response_model=PlaceOut)
def update_place(project_id: int, place_id: int, payload: PlaceUpdate, session: Session = Depends(get_session)):
    place = session.get(ProjectPlace, place_id)
    if not place or place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found")

    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(place, field_name, value)

    session.add(place)
    session.commit()
    session.refresh(place)

    project = session.get(TravelProject, project_id)
    if project.places and all(p.visited for p in project.places):
        project.completed = True
        session.add(project)
        session.commit()

    return place