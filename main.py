from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from common.middleware import CustomMiddleware
from event.routes import event_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic goes here
    print("Starting up...")
    # Yield control back to FastAPI while the app is running
    yield
    # Shutdown logic goes here
    print("Shutting down...")
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