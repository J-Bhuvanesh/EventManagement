from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from common.middleware import CustomMiddleware
from event.routes import event_router
from event.views import run_auto_complete

# Scheduler setup
scheduler = AsyncIOScheduler()
scheduler.add_job(run_auto_complete, 'interval', minutes=1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

# FastAPI app setup
app = FastAPI(lifespan=lifespan)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(CustomMiddleware)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Event Management System!"}

# Include Routes
app.include_router(event_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
