from fastapi import FastAPI

app = FastAPI(title="Asset Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "asset-service"}

@app.get("/")
def root():
    return {"message": "Asset Service running"}
