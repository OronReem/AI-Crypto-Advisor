"""The expected shape of each request body.

FastAPI reads these classes and rejects a malformed request before the route
function runs, which is also where the quiz answer limits are enforced.
"""

from typing import Literal  # restricts a field to a fixed set of exact values

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class QuizAnswers(BaseModel):
    coins: list[str] = Field(min_length=1, max_length=5)
    investor_type: str
    content_types: list[str] = Field(min_length=1, max_length=4)


class VoteRequest(BaseModel):
    section: str
    topic: str
    item: str
    direction: Literal["up", "down"]
