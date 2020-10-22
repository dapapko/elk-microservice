import typing
from fastapi import FastAPI, Response, status,  HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel as BM
from models import *
from routes import auth, faculty, educational_program, department, group, course
import bcrypt
import jwt
from jwt import PyJWTError
import os



app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/get_token')


def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv('APP_KEY'))
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = User.get(email=email)
    if user is None:
        raise credentials_exception
    return user


class UserRegistration(BM):
    name: str
    email: str
    password: str
    role: str
    faculty: int
    department: typing.Optional[str] = None
    edu_program: typing.Optional[int] = None
    group: typing.Optional[int] = None
    token:str



app.include_router(
    auth.router,
    prefix='/v1/auth',
    tags=["Users"]
)
app.include_router(group.router, tags=["Group"])
app.include_router(faculty.router, tags=["Faculty"])
app.include_router(department.router, tags=["Department"])
app.include_router(course.router, tags=["Course"])
app.include_router(educational_program.router, tags=["Educational program"])


# get
@app.get("/")
def home():
    return {"Hello": "World"}



@app.post("/user/register")
@db_session
def user_registration(req: UserRegistration, response: Response):
    user = get_current_user(req.token)
    if count(u for u in User if u.email == req.email) > 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "User with such email is already registered"}
    salt = bcrypt.gensalt()
    passwd = bcrypt.hashpw(req.password.encode("utf-8"), salt)
    user = User(name=req.name, password=passwd.decode("utf-8"), email=req.email, salt=salt.decode("utf-8"))
    user.role = Role.get(name=req.role)
    try:
        user.faculty = Faculty[req.faculty]
        if req.department is not None: user.departments.add(Department.get(name=req.department))
        if req.edu_program is not None: user.educational_program = Educational_program[req.edu_program]
        if req.group is not None: user.groups.add(Group[req.group])
    except ObjectNotFound:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Faculty, group, department or educational program with such ID doesn't exist"}
    commit()
    return {"status": "ok"}

