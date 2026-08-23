import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from pwdlib import PasswordHash

from schema.schemas import individual_user_serializer


load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_dir, '../database')

from database.configurations import user_db

# Password hashing
password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash('dummypassword')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

# User Auth Bodies
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

# OAuth2 User Functions
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def get_user(db, username: str) -> dict | None:
    # Queries MongoDB for a document containing the username key (e.g., {'wildAstroboy': {'$exists': true}})
    raw_user = await db.find_one({username: {'$exists': True}})
    if raw_user:
        return individual_user_serializer(raw_user)
    return None

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

async def get_password_hash(password):
    return password_hash.hash(password)

async def authenticate_user(db, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(user_db['collection'], username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    if current_user.get('disabled'):
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user