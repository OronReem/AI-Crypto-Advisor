"""Password hashing and JWT tokens.

Everything here answers one of two questions: is this the right password, and
who is making this request?
"""

import os  # reads JWT_SECRET from the environment
from datetime import datetime, timedelta, timezone  # builds the token's expiry time

import jwt  # creates and verifies JWTs (PyJWT)
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # reads the auth header
from passlib.context import CryptContext  # hashes and checks passwords
from sqlalchemy.orm import Session

from database import engine
from tables import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()


# builds a signed token that identifies this user for the next 24 hours
def create_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")


# checks a request's token is genuine and unexpired, returns the matching user
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # checks the token is real and not too old, then reads what's inside it
        payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = int(payload["sub"])
    with Session(engine) as session:
        user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user
