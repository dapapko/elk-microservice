from fastapi import APIRouter, Response, status
from pydantic import BaseModel as BM
import typing
from main import get_current_user
router = APIRouter()
from models import *
import json


class FacultyCreationRequest(BM):
    name: str
    token:str


class FacultyCreationResponse(BM):
    error: typing.Optional[str] = None


@router.post("/faculty", response_model=FacultyCreationResponse)
@db_session
def create_faculty(req: FacultyCreationRequest, response: Response):
    user = get_current_user(req.token)
    if count(f for f in Faculty if f.name == req.name) > 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Faculty with this name already exists"}
    fac = Faculty(name=req.name)
    commit()


@router.delete("/faculty/{faculty_id}")
@db_session
def delete_faculty(faculty_id: int, response: Response):
    try:
        Faculty[faculty_id].delete()
    except ObjectNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Department with id {faculty_id} doesn't exists"}


@router.get("/faculty")
@db_session
def list_faculties():
    faculties = select(f for f in Faculty)[:]
    return json.dumps([f.to_dict() for f in faculties])

@router.put("/faculty/{faculty_id}")
@db_session
def update_faculty(faculty_id: int, req: FacultyCreationRequest):
    user = get_current_user(req.token)
    f = Faculty[faculty_id]
    f.name = req.name
    commit()
