from fastapi import HTTPException
from dotenv import load_dotenv
import bcrypt
from fastapi import Security
from pydantic import BaseModel as BM
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
import os
from models import *
load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/get_token')


class Auth:
    def __init__(self):
        self.db = Database()
        self.key = os.getenv('APP_KEY')

    class LoginModel(BM):
        email:str
        password:str

    @db_session
    def login(self, email:str, password:str):
        print(email)
        usr = User.get(email=email)
        print(usr)
        if bcrypt.checkpw(password.encode("utf-8"), usr.password.encode("utf-8")):
            token = jwt.encode({
                'sub': usr.email,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=21600),
                'fln': usr.name
            },
                self.key)

            return {"status": "success", "token": token.decode('utf-8')}
        return {"status": "error", "message": "username/password incorrect"}

    def validate(self, token):
        try:
            data = jwt.decode(token, self.key)
        except Exception as e:
            if "expired" in str(e):
                raise HTTPException(status_code=400, detail={"status": "error", "message": "Token expired"})
            else:
                raise HTTPException(status_code=400, detail={"status": "error", "message": "Exception: " + str(e)})
        return data

