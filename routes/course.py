from fastapi import APIRouter, Response, status, HTTPException
from pydantic import BaseModel as BM
import typing
import  helpers
router = APIRouter()
from models import *
import json


def get_by_id(id:int, model):
    try:
        obj = model[id]
    except ObjectNotFound:
        raise HTTPException(404, f"{model.__class__.__name__} not found")
    return obj


class AssignRequest(BM):
    course:int
    users: typing.Optional[typing.List[int]] = None
    token:str


class FilterRequest(BM):
    user: typing.Optional[int] = None
    group: typing.Optional[int] = None
    token: str


class CourseCreationRequest(BM):
    name: str
    year: str
    department:int
    program: int
    token:str
    credits:int


@router.post("/course")
@db_session
def create_course(req: CourseCreationRequest):
    user = helpers.get_current_user(req.token)
    dep = helpers.get_by_id(req.department, Department)
    program = get_by_id(req.program, Educational_program)
    course = Course(name=req.name, year=req.year, credits=req.credits, department=dep)
    course.program = program.name
    commit()



@router.post('/course/assign')
@db_session
def assign_user_to_course(req: AssignRequest):
    helpers.get_current_user(req.token)
    course = helpers.get_by_id(req.course, Course)
    users = User.select(lambda u: u.id in req.users)
    for user in users:
        course.users.add(user)
    commit()


@router.post('/course/unsubscribe')
@db_session
def unsubscribe_user_from_course(req: AssignRequest):
    course = helpers.get_by_id(req.course, Course)
    users = User.select(lambda u: u.id in req.users and course in u.courses)
    for u in users:
        u.courses.remove(course)
    commit()



@router.get("/course/{course_id}")
@db_session
def get_course(course_id:int):
    return json.dumps(get_by_id(course_id, Course).to_dict())


@router.post("/course/get")
@db_session
def get_courses_by(req: FilterRequest):
    usr = helpers.get_current_user(req.token)
    if req.group is not None:
        group = Group[req.group]
        courses = select(c for c in Course if group in c.users.groups)[:]
    elif req.user is not None:
        user = User[req.user]
        courses = select(c for c in Course if user in c.users)
    return json.dumps([c.to_dict() for c in courses])



@router.delete("/course/{course_id}")
@db_session
def delete_course(course_id: int, response: Response):
    try:
        Course[course_id].delete()
    except ObjectNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Course with id {course_id} doesn't exists"}


@router.get("/course")
@db_session
def list_courses():
    courses = select(c for c in Course)[:]
    return json.dumps([c.to_dict() for c in courses])


@router.put("/course/{course_id}")
@db_session
def update_course(course_id: int, req: CourseCreationRequest):
    user = helpers.get_current_user(req.token)
    course = get_by_id(course_id, Course)
    course.name = req.name
    course.credits = req.credits
    course.year = req.year
    course.department = req.department
    commit()
