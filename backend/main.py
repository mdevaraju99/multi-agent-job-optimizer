from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import data_routes, optimization_routes, simulation_routes

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_routes.router, prefix=settings.API_PREFIX)
app.include_router(optimization_routes.router, prefix=settings.API_PREFIX)
app.include_router(simulation_routes.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Multi-Agent Job Optimizer API",
        "docs": "/docs",
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # Force reload trigger
