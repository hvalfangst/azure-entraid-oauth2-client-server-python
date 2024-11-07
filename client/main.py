# client/main.py

from fastapi import FastAPI
from client.routers import auth, heroes

app = FastAPI(
    title="Hvalfangst Client",
    description="Client accessing our server deployed on Azure Web Apps secured by OAuth 2.0 authorization code flow with OIDC",
    version="1.0.0"
)

# Register the oauth and heroes router
app.include_router(auth.router, prefix="/auth", tags=["OAuth2 Back-channel"])
app.include_router(heroes.router, prefix="/api", tags=["Heroes"])
