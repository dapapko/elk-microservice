from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from .auth_check import Auth

router = APIRouter()
auth = Auth()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/get_token')


class Users(BaseModel):
    message: str


async def is_auth(token: str = Security(oauth2_scheme)):
    return auth.validate(token)


@router.get(
    '/',
    response_model=Users,
    response_description="Returns list of users",
    summary="Return a list of users",
    description="Return a list of users"
)
async def get_users(*, token: str = Security(is_auth)):
    return {"message": "authorized"}
