from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    user_email: str | None
    outcome: str
    detail: str | None
    created_at: str

    class Config:
        from_attributes = True