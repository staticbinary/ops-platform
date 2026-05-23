import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Asset
from .schemas import AssetCreate, AssetUpdate, AssetResponse

app = FastAPI(
    title="Asset Service",
    description="Operations platform asset management service",
    version="1.0.0",
    root_path="/api/assets"
)

SECRET_KEY = "dev-secret-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

Base.metadata.create_all(bind=engine)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())

    print(f"[request_id={request_id}] Incoming request: {request.method} {request.url}")

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    print(f"[request_id={request_id}] Completed response: {response.status_code}")

    return response


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "asset-service"}


@app.get("/db-health", tags=["Health"])
def db_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "error",
            "database": str(e)
        }


@app.post("/assets", response_model=AssetResponse, tags=["Assets"])
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    db_asset = Asset(
        hostname=asset.hostname,
        owner=asset.owner,
        status=asset.status
    )

    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset


@app.get("/assets", response_model=list[AssetResponse], tags=["Assets"])
def get_assets(db: Session = Depends(get_db)):
    return db.query(Asset).all()


@app.get("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@app.put("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
def update_asset(
    asset_id: int,
    updated_asset: AssetUpdate,
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset.hostname = updated_asset.hostname
    asset.owner = updated_asset.owner
    asset.status = updated_asset.status

    db.commit()
    db.refresh(asset)

    return asset


@app.delete("/assets/{asset_id}", tags=["Assets"])
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(asset)
    db.commit()

    return {"message": f"Asset {asset_id} deleted successfully"}


@app.post("/auth/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "password":
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={"sub": form_data.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/auth/me", tags=["Auth"])
def read_me(current_user: str = Depends(verify_token)):
    return {
        "username": current_user
    }


@app.get("/", tags=["Root"])
def root():
    return {"message": "Asset Service running"}