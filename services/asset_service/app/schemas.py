from pydantic import BaseModel


class AssetCreate(BaseModel):
    hostname: str
    owner: str
    status: str


class AssetResponse(BaseModel):
    id: int
    hostname: str
    owner: str
    status: str

    class Config:
        from_attributes = True


class AssetUpdate(BaseModel):
    hostname: str
    owner: str
    status: str