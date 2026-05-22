from sqlalchemy import Column, Integer, String

from .database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, unique=True, index=True)
    owner = Column(String)
    status = Column(String)