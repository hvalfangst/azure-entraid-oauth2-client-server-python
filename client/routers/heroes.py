import os
from http.client import HTTPException
from typing import List

import httpx
from fastapi import APIRouter, HTTPException

from client.logger import logger
from client.models import Hero
from client.services.token_storage import get_stored_token  # Import get_stored_token function

router = APIRouter()

# Set values based on environment variable or hard-coded URL
BACKEND_API_BASE_URL = os.getenv("HVALFANGST_API_URL", "https://hvalfangstlinuxwebapp.azurewebsites.net/api")


# Helper function to make HTTP requests to the backend API
async def request_backend(method: str, endpoint: str, json=None):
    url = f"{BACKEND_API_BASE_URL}{endpoint}"

    # Retrieve the access token from token storage
    token_data = get_stored_token()
    headers = {"Authorization": f"Bearer {token_data}"} if token_data else {}

    # Log the request details
    logger.info(f"Preparing {method} request to URL: {url}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Payload: {json}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, json=json, headers=headers)
            response.raise_for_status()
            logger.info(f"Request to {url} completed successfully with status code {response.status_code}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred for {method} request to {url}: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# POST: Create a new Hero
@router.post("/heroes/", response_model=Hero)
async def create_hero(hero: Hero):
    return await request_backend("POST", "/heroes/", json=hero.dict())


# GET: Retrieve a hero by ID
@router.get("/heroes/{hero_id}", response_model=Hero)
async def read_hero(hero_id: str):
    return await request_backend("GET", f"/heroes/{hero_id}")


# GET: Retrieve all heroes
@router.get("/heroes/", response_model=List[Hero])
async def read_heroes():
    return await request_backend("GET", "/heroes/")


# DELETE: Delete a hero by ID
@router.delete("/heroes/{hero_id}", response_model=dict)
async def delete_hero(hero_id: str):
    return await request_backend("DELETE", f"/heroes/{hero_id}")
