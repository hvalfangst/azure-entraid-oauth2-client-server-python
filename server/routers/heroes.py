from http.client import HTTPException
from typing import List
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from models import *
from services import *
from security.jwt_utils import oauth2_scheme
from security.auth import authorize
from config.config import AzureConfig

router = APIRouter()
hero_service = HeroService()



# POST: Create a new Hero
@router.post("/heroes/", response_model=Hero)
async def create_hero(hero: Hero, token: str = Depends(oauth2_scheme)):
    await authorize(token, ["Heroes.Write"])
    return await hero_service.create_hero(hero)


# GET: Retrieve a hero by ID
@router.get("/heroes/{hero_id}", response_model=Hero)
async def read_hero(hero_id: str, token: str = Depends(oauth2_scheme)):
    await authorize(token, ["Heroes.Read"])
    hero = await hero_service.get_hero(hero_id)
    if hero:
        return hero
    else:
        raise HTTPException(status_code=404, detail="Hero not found")


# GET: Retrieve all heroes
@router.get("/heroes/", response_model=List[Hero])
async def read_heroes(token: str = Depends(oauth2_scheme)):
    await authorize(token, ["Heroes.Read"])
    return await hero_service.list_heroes()


# DELETE: Delete a hero by ID
@router.delete("/heroes/{hero_id}", response_model=dict)
async def delete_hero(hero_id: str, token: str = Depends(oauth2_scheme)):
    await authorize(token, ["Heroes.Delete"])
    success = await hero_service.delete_hero(hero_id)
    if success:
        return {"message": f"Hero with id '{hero_id}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Hero not found")