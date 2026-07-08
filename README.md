# Travel Planner API

A CRUD API for managing travel projects and places, built with FastAPI, SQLModel, and SQLite. Validates places against the Art Institute of Chicago public API before adding them to a project.

## Setup

1. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python3 -m uvicorn main:app --reload
```

4. Open the interactive API docs:
   http://127.0.0.1:8000/docs
## Project structure

- `main.py` — API routes
- `models.py` — database models (SQLModel)
- `schemas.py` — request/response models (Pydantic)
- `database.py` — database connection setup
- `external_api.py` — Art Institute of Chicago API integration

## Business rules implemented

- A project can hold up to 10 places
- The same external place cannot be added to the same project twice
- Places are validated against the Art Institute of Chicago API before being stored
- A project cannot be deleted while it has any visited places
- A project is automatically marked `completed` once all its places are marked `visited`

## Example flow

1. `POST /projects` — create a project (with or without an initial list of places)
2. `POST /projects/{project_id}/places` — add a place by its Art Institute of Chicago artwork ID (e.g. `27992`)
3. `PATCH /projects/{project_id}/places/{place_id}` — update notes or mark a place as visited
4. `GET /projects/{project_id}` — view the project, including its places and completion status

## Notes / assumptions

- The task description mentions a minimum of 1 place per project; the API allows creating a project without places first and adding them afterward, since project creation and place creation are listed as separate capabilities. A project simply won't be marked `completed` until it has at least one visited place.
- SQLite is used for simplicity, as permitted by the task requirements.

## Possible next steps (not implemented due to time constraints)

- Pagination and filtering for listing endpoints
- Caching responses from the Art Institute API
- Basic authentication
- Docker setup
