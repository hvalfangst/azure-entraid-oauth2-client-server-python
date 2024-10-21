import json
from typing import List, Dict, Any

import httpx
from fastapi import HTTPException
from jwt.algorithms import RSAAlgorithm
from logger import *
from models import *
from starlette import status

from .token_validator import get_openid_config


async def fetch_jwk_for_kid(kid: str) -> dict:
    """
    Fetches the JWK (JSON Web Key) for the given key ID (kid).
    Retrieves a list of public JWKs from the OpenID configuration, then matches the 'kid'.
    """
    logger.info("Fetching JWKs from OpenID configuration.")
    public_jwks = await get_public_jwks()
    logger.info(f"Fetched {len(public_jwks)} JWKs.")

    jwk = next((jwk for jwk in public_jwks if jwk['kid'] == kid), None)
    if not jwk:
        logger.error(f"No JWK found for kid: {kid}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Public key not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"Matching JWK found for kid: {kid}")
    return jwk


def convert_jwk_to_rsa_public_key(jwk: dict) -> RSAAlgorithm:
    """
    Converts a JWK (JSON Web Key) to an RSA public key.
    """
    logger.info("Converting JWK to RSA public key.")
    rsa_public_key = RSAAlgorithm.from_jwk(json.dumps(jwk))
    logger.info("Conversion to RSA public key completed.")
    return rsa_public_key


async def get_public_jwks() -> List[Dict[str, Any]]:
    """
    Fetches public keys from the OpenID configuration.

    Returns:
        List of dictionaries, each representing a public key.
    """
    logger.info("Fetching public keys from OpenID configuration.")
    try:
        config: Dict[str, Any] = await get_openid_config()
        logger.info(config)

        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(config["jwks_uri"])
            response.raise_for_status()
            keys: List[Dict[str, Any]] = response.json()["keys"]
            logger.info(f"Fetched {len(keys)} public keys.")

            # Log Key IDs
            for key in keys:
                logger.info(f"Key ID (kid): {key.get('kid')}")

            return keys

    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch public keys: {e}")
        raise
    except Exception as e:
        logger.exception(f"An unexpected error occurred while fetching public keys: {e}")
        raisexception(f"An unexpected error occurred while fetching public keys: {e}")
        raise
