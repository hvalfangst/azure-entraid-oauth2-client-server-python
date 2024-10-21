import logging
from typing import List

import httpx
from logger import *
from models import *
from config.config import AzureConfig

logger = logging.getLogger("token_validator")


# Get the OpenID configuration with public keys
async def get_openid_config():
    logger.info("Fetching OpenID configuration.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AzureConfig.AUTHORITY}/v2.0/.well-known/openid-configuration")
            response.raise_for_status()
            logger.info("Successfully fetched OpenID configuration.")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch OpenID configuration: {e}")
        raise
    except Exception as e:
        logger.exception(f"An unexpected error occurred while fetching OpenID configuration: {e}")
        raise


# Helper function to check for required roles
def has_required_roles(decoded_token: DecodedToken, required_roles: List[str]) -> bool:
    if decoded_token.roles:
        return any(role in decoded_token.roles for role in required_roles)
    return False
