from fastapi import APIRouter, Response, status
from pydantic import BaseModel as BM
import typing
import helpers
from models import *
router = APIRouter()


class EduProgramCreationRequest(BM):
    name: str
    faculty: typing.Optional[int] = None
    token: str


class AssignRequest(BM):
    program: int
    user: typing.List[int]
    token:str


@router.post("/ep")
@db_session
def create_program(req: EduProgramCreationRequest, resp: Response):
    if count(e for e in Educational_program if e.name == req.name) > 0:
        resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error":"Educational program with such name already exists"}
    user = helpers.get_current_user(req.token)
    fac = helpers.get_by_id(req.faculty, Faculty)
    ep = Educational_program(name=req.name, faculty=fac)
    commit()


@router.delete("/ep/{ep_id}")
@db_session
def delete_ep(ep_id: int, response: Response):
    try:
        Educational_program[ep_id].delete()
    except ObjectNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Educational program with id {ep_id} doesn't exists"}


@router.put("/update/{ep_id}")
@db_session
def update_ep(ep_id: int, req: EduProgramCreationRequest):
    user = helpers.get_current_user(req.token)
    ep = helpers.get_by_id(ep_id, Educational_program)
    ep.name = req.name
    commit()


@router.post('/ep/assign')
@db_session
def assign_user_to_ep(req: AssignRequest):
    students = select(u for u in User if u.id in req.user)
    ep = helpers.get_by_id(req.program, Educational_program)
    for s in students:
        s.educational_program = ep
    commit()


@router.post('/ep/unlink', summary="Unlink user from educational program")
@db_session
def unlink_user_from_ep(req: AssignRequest):
    students = select(u for u in User if u.id in req.user and u.educational_program == req.program)
    ep = helpers.get_by_id(req.program, Educational_program)
    for s in students:
        ep.users.remove(s)
        s.educational_program = None
