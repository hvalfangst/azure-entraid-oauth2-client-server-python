from fastapi import FastAPI

from logger import logger
from routers import heroes

app = FastAPI(
    title="Hero API",
    description="An API to manage heroes secure by OAuth 2.0 auth code flow",
    version="1.0.0"
)

logger.info("Starting up API")


@app.get("/")
async def index():
    return "Hvalfangst FastAPI deployed to Azure App Service"


app.include_router(heroes.router, prefix="/api", tags=["Heroes"])
