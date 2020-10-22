from datetime import datetime
from pony.orm import *
import os


db = Database()

class Course(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    credits = Optional(int)
    users = Set('User')
    year = Optional(str)
    program = Optional(str)
    department = Required('Department')
    questions = Set('Question')
    final_grades = Set('FinalGrade')


class Faculty(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    users = Set('User')
    departments = Set('Department')
    educational_programs = Set('Educational_program')


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    email = Optional(str)
    password = Optional(str)
    token = Optional(str, nullable=True)
    api_token = Optional(str, nullable=True)
    salt = Optional(str, nullable=True)
    courses = Set(Course)
    faculty = Optional(Faculty)
    educational_program = Set('Educational_program')
    groups = Set('Group')
    works = Set('Work')
    variants = Set('Variant')
    final_grades = Set('FinalGrade')
    attempts = Set('Attempt')
    roles = Set('Role')
    departments = Set('Department')


class Department(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    faculty = Required(Faculty)
    courses = Set(Course)
    users = Set(User)


class Educational_program(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    faculty = Required(Faculty)
    users = Set(User)
    groups = Set('Group')


class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    users = Set(User)
    educational_program = Optional(Educational_program)


class Question(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Optional(str)
    complexity = Required(int)
    content = Required(LongStr)
    course = Required(Course)
    options = Optional(Json)
    answer = Optional(Json)


class Variant(db.Entity):
    id = PrimaryKey(int, auto=True)
    variant = Optional(Json)
    work = Required('Work')
    user = Required(User)


class Work(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    weight = Required(float)
    users = Set(User)
    variants = Set(Variant)
    attempts = Set('Attempt')
    duration = Optional(datetime)
    deadline = Optional(datetime)
    registration_start = Optional(datetime)
    registration_end = Optional(datetime)


class FinalGrade(db.Entity):
    id = PrimaryKey(int, auto=True)
    grade = Optional(int)
    user = Required(User)
    course = Required(Course)


class Attempt(db.Entity):
    id = PrimaryKey(int, auto=True)
    answer = Optional(Json)
    work = Required(Work)
    user = Required(User)
    stat = Optional(Json)
    grade = Optional(float)
    start = Required(datetime)
    end = Optional(datetime)
    duration = Optional(datetime)


class Role(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    users = Set(User)

db.bind(provider='postgres', user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'), database=os.getenv('DB_NAME'))
try:
    db.generate_mapping(create_tables=True)
except Exception as ex:
    pass
