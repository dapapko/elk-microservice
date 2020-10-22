from fastapi import HTTPException, status
import jwt
from pony.orm import ObjectNotFound
from models import User
import os
from pony.orm import *

@db_session
def get_by_id(id:int, model):
    try:
        obj = model[id]
    except ObjectNotFound:
        raise HTTPException(404, f"{model.__class__.__name__} not found")
    return obj

@db_session
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
    except jwt.PyJWTError:
        raise credentials_exception
    user = User.get(email=email)
    if user is None:
        raise credentials_exception
    return user