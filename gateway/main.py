"""FastAPI application entrypoint for the agent gateway."""
from __future__ import annotations

from fastapi import FastAPI

from gateway.routes import router as rest_router
from gateway.websocket import router as ws_router

app = FastAPI(title="AI Agent Gateway", version="0.1.0")
app.include_router(rest_router)
app.include_router(ws_router)
