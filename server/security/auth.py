from typing import List

from fastapi import HTTPException
from logger import *
from models import *
from starlette import status
from .jwt_utils import verify_token_signature


async def authorize(token: str, required_scopes: List[str]):
    """
    Verifies that the provided token contains the required scopes for the action.
    """
    # Decode and verify the token
    decoded_token = await verify_token_signature(token)

    logger.info(decoded_token)

    # Check if the token includes all required scopes
    missing_scopes = [scope for scope in required_scopes if scope not in decoded_token.get_scopes()]
    if missing_scopes:
        logger.error(f"Token missing required scopes: {missing_scopes}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient scope",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log success if the token has all required scopes
    logger.info(f"Token has required scopes: {required_scopes}.")
