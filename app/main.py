"""Minimal FastAPI service for ECS Fargate deployment."""

from fastapi import FastAPI

app = FastAPI(title="Audi Fargate Service", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Health check endpoint expected by the Application Load Balancer."""

    return {"status": "ok"}


@app.get("/")
def read_root() -> dict[str, str]:
    """Simple landing endpoint to verify the service is reachable."""

    return {"message": "Hello from AWS Fargate!"}

