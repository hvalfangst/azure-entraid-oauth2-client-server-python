from fastapi import FastAPI

from logger import logger
from routers import heroes

app = FastAPI(
    title="Hvalfangst Resource Server",
    description="Resource server API protected by Oauth 2.0 scopes",
    version="1.0.0"
)

logger.info("Starting up API")


@app.get("/")
async def index():
    return "Hvalfangst FastAPI deployed to Azure App Service"


app.include_router(heroes.router, prefix="/api", tags=["Heroes"])
