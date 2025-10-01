import logging

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from server.simulation.Simulation import simulation
from server.web_api.api import api

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await simulation.start()
    yield
    logger.info("Shutting down WavesLab simulation environment...")
    await simulation.stop()

api.app.router.lifespan_context = lifespan

app = api.app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)