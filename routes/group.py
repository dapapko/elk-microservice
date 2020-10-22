from fastapi import APIRouter, Response, status, HTTPException
from pydantic import BaseModel as BM
import typing
import helpers
router = APIRouter()
from models import *
import json


def get_by_id(id:int, model):
    try:
        obj = model[id]
    except ObjectNotFound:
        raise HTTPException(404, f"{model.__class__.__name__} not found")
    return obj


class GroupCreationRequest(BM):
    name: str
    faculty: int
    program: int
    token:str


class AssignRequest(BM):
    group:int
    user:typing.List[int]
    token:str

@router.post("/group")
@db_session
def create_group(req: GroupCreationRequest):
    user = helpers.get_current_user(req.token)
    edu_program = helpers.get_by_id(req.faculty, Educational_program)
    group = Group(name=req.name, educational_program=edu_program)
    commit()



@router.delete("/group/{group_id}")
@db_session
def delete_group(group_id: int, response: Response):
    try:
        Group[group_id].delete()
    except ObjectNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Group with id {group_id} doesn't exists"}


@router.get("/group")
@db_session
def list_groups():
    groups = select(g for g in Group)[:]
    return json.dumps([g.to_dict() for g in groups])



@router.post('/group/assign')
@db_session
def assign_user_to_group(req: AssignRequest):
    helpers.get_current_user(req.token)
    group = helpers.get_by_id(req.group, Group)
    students = select(u for u in User if u.id in req.user and group not in u.groups)
    for s in students:
        group.users.add(s)
        s.groups.add(group)
    commit()


@router.post('/group/unlink')
@db_session
def unlink_user_from_group(req: AssignRequest):
    helpers.get_current_user(req.token)
    group = helpers.get_by_id(req.group, Group)
    students = select(u for u in User if u.id in req.user and group in u.groups)
    for s in students:
        group.users.remove(s)
        s.groups.remove(group)
    commit()

