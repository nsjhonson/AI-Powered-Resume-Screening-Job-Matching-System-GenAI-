from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="AI-Powered Resume Screening System")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the AI-Powered Resume Screening System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
