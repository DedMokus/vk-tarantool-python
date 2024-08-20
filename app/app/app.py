import asynctnt.exceptions
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from typing import Dict, List
from pydantic import BaseModel

import jwt
import time
import os
import asynctnt


JWT_SECRET = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("ALGORITHM")
TNT_USER = os.getenv("DB_USER_NAME")
TNT_PASSWORD = os.getenv("DB_USER_PASSWORD")

app = FastAPI()


async def get_tarantool_connection():
    try:
        conn = asynctnt.Connection(host="tarantool-storage", port=3301, username=TNT_USER, password=TNT_PASSWORD)
        await conn.connect()
        yield conn
    finally:
        await conn.disconnect()
        conn.close()

users = [('admin', 'presale')]

def check_user(username, password):
    if (username, password) in users:
        return True

def token_response(token: str):
    return {
        "token": token
    }

def sign_jwt(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)
    
def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
    
class UserSchema(BaseModel):
    username: str
    password: str

class DataModelWrite(BaseModel):
    data: Dict[str,str]

class DataModelRead(BaseModel):
    keys: List[str]

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


@app.post("/app/login")
async def login(user: UserSchema):
    if check_user(user.username, user.password):
        return sign_jwt(user.username)
    else:
        return HTTPException(status_code=403, detail="Invalid username or password")
    


@app.post("/app/write", dependencies=[Depends(JWTBearer())])
async def tnt_insert(data: DataModelWrite, conn=Depends(get_tarantool_connection)):
    try:
        res = [await conn.insert('kv', item) for item in list(data.data.items())]
        return {"status": "success"}
    except asynctnt.exceptions.TarantoolDatabaseError as e:
        return {"Database Error": e.message}

    

@app.post("/app/read", dependencies=[Depends(JWTBearer())])
async def tnt_select(keys: DataModelRead, conn=Depends(get_tarantool_connection)):
    try:
        data = {"data": {}}
        for key in keys.keys:
            response = await conn.select('kv', [key])
            if not response.body:
                data['data'][key] = None
            else:
                data["data"].update(response)
        return data
    except Exception as e:
        return e
