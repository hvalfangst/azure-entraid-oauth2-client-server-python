import webbrowser
from typing import List
from urllib.parse import urlencode
import httpx
import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from client.config import oauth_settings
from client.logger import logger
from client.services.token_storage import store_token

AUTHORITY = f"https://login.microsoftonline.com/{oauth_settings.AZURE_TENANT_ID}"
AUTH_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"
JWKS_URL = f"https://login.microsoftonline.com/{oauth_settings.AZURE_TENANT_ID}/discovery/v2.0/keys"

# OAuth2AuthorizationCodeBearer scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=AUTH_URL,
    tokenUrl=TOKEN_URL
)

# Prepare the parameters for the OAuth2 authorization URL
query_params = {
    "client_id": oauth_settings.AZURE_CLIENT_ID,
    "response_type": "code",
    "scope": oauth_settings.SCOPES,
    "response_mode": "query"
}

# Encode the query parameters and construct the full authorization URL
login_url = f"https://login.microsoftonline.com/{oauth_settings.AZURE_TENANT_ID}/oauth2/v2.0/authorize?{urlencode(query_params)} "

# Open the login URL in the default web browser
webbrowser.open_new_tab(login_url)


async def handle_openid_connect_flow(code: str):
    """
    Handle OpenID Connect flow by exchanging the authorization code for tokens,
    decoding the ID token, and verifying the token.
    """
    # Exchange the authorization code for access and ID tokens
    try:
        logger.info("Attempting to request access token")

        # Exchange code for token
        token = await get_access_token(code)

        # Attempt to fetch id and access token from the results
        logger.info("Attempting to fetch id_token from token")
        id_token = token.get("id_token")
        logger.info("Attempting to fetch access_token from token")
        access_token = token.get("access_token")

        if not id_token:
            raise HTTPException(status_code=400, detail="ID token not found in response")

        # Decode id and access tokens - signature verification will be done on the server
        decoded_id_token = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["RS256"])
        decoded_access_token = jwt.decode(access_token, options={"verify_signature": False}, algorithms=["RS256"])
        print("Decoded ID Token:", decoded_id_token)
        print("Decoded access Token:", decoded_access_token)

        # Set the access token variable in our token storage class (used in subsequent HTTP calls to our server)
        store_token(access_token)

        return {
            "id_token": decoded_id_token,
            "access_token": decoded_access_token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


async def get_access_token(code: str):
    """Exchange authorization code for an access token."""

    logger.info("Starting authorization code exchange for access token")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                TOKEN_URL,
                data={
                    'client_id': oauth_settings.AZURE_CLIENT_ID,
                    'client_secret': oauth_settings.AZURE_CLIENT_SECRET,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': oauth_settings.REDIRECT_URI
                },
            )

            logger.info(f"Token endpoint responded with status code: {response.status_code}")

            response_data = response.json()
            logger.info(f"Response data: {response_data}")

            if response.status_code != 200:
                logger.error(f"Failed to exchange code for token. Error: {response_data}")
                raise HTTPException(status_code=response.status_code, detail=response_data)

            return response_data

        except Exception as e:
            logger.exception(f"An error occurred during token exchange: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred during the token exchange process")


def has_required_scope(token_scopes: List[str], required_scopes: List[str]) -> bool:
    """Check if any of the token's scopes fulfill the required scopes based on the role hierarchy."""
    logger.debug(f"Checking scopes: Token scopes: {token_scopes}, Required scopes: {required_scopes}")

    for token_scope in token_scopes:
        # Log which role (token scope) is being checked
        logger.debug(f"Checking token scope: {token_scope}")

        # Check if the token scope can fulfill the required scope using the role hierarchy
        for required_scope in required_scopes:
            if required_scope in token_scope:
                logger.info(
                    f"Scope match: Token scope '{token_scope}' grants access to required scope '{required_scope}' "
                    f"based on the role hierarchy.")
                return True
            else:
                logger.debug(f"Token scope '{token_scope}' does not grant access to required scope '{required_scope}'.")

    # If no scopes satisfy the requirement, return False
    logger.warning(f"No token scopes match the required scopes: {required_scopes}")
    return False


async def verify_scope(required_scopes: List[str]):
    logger.info("Starting scope verification")

    try:
        # Ensure there's a decoded token available for verification
        if DECODED_TOKEN is None:
            logger.error("No token stored for scope verification")
            raise HTTPException(status_code=401, detail="No token available for verification")

        # Extract the scopes from the stored decoded token (from 'scp' field)
        token_scopes = DECODED_TOKEN.get("scp", "").split()
        logger.debug(f"Token scopes extracted: {token_scopes}")
        logger.debug(f"Required scopes for operation: {required_scopes}")

        # Check if the token has the required scope based on role hierarchy
        if has_required_scope(token_scopes, required_scopes):
            logger.info(f"Scope verification successful. Token has the required scopes for the operation.")
            return DECODED_TOKEN
        else:
            logger.warning(f"Scope verification failed. Required: {required_scopes}, Found: {token_scopes}")
            raise HTTPException(status_code=403, detail="Insufficient scope for this operation")

    except Exception as e:
        logger.error(f"Error during scope verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify scope")
