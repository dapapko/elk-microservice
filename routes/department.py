from fastapi import APIRouter, Response, status
from pydantic import BaseModel as BM
import typing
from main import get_current_user
router = APIRouter()
from models import *
import json


class DepartmentCreationRequest(BM):
    name: str
    faculty: int
    token:str


@router.post("/department")
@db_session
def create_department(req: DepartmentCreationRequest, response: Response):
    user = get_current_user(req.token)
    if count(d for d in Department if d.name == req.name) > 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Department with this name already exists"}
    dep = Department(name=req.name, faculty=Faculty[req.faculty])
    commit()


@router.delete("/department/{department_id}")
@db_session
def delete_department(department_id: int, response: Response):
    try:
        Department[department_id].delete()
    except ObjectNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Department with id {department_id} doesn't exists"}


@router.get("/department")
@db_session
def list_departments():
    departments = select(d for d in Department)[:]
    return json.dumps([d.to_dict() for d in departments])


@router.put("/department/{department_id}")
@db_session
def update_department(department_id: int, req: DepartmentCreationRequest, resp: Response):
    user = get_current_user(req.token)
    try:
        dep = Department[department_id]
        fac = Faculty[req.faculty]
    except ObjectNotFound:
        resp.status_code = status.HTTP_404_NOT_FOUND
        return None
    dep.name = req.name
    dep.faculty = fac
    commit()