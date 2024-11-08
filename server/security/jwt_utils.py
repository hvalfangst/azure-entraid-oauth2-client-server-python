import base64
import json
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt import ExpiredSignatureError, MissingRequiredClaimError, PyJWTError
from logger import *
from models import *
from starlette import status
from .jwk_utils import fetch_jwk_for_kid, convert_jwk_to_rsa_public_key
from config.config import AzureConfig

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{AzureConfig.AUTHORITY}/oauth2/v2.0/authorize",
    tokenUrl=f"{AzureConfig.AUTHORITY}/oauth2/v2.0/token"
)


async def verify_token_signature(token: str = Depends(oauth2_scheme)) -> DecodedToken:
    """
    Verifies the signature of a JWT and returns the decoded claims if valid.
    """
    try:
        logger.info("Starting token verification process.")

        # Step 1: Base64-decode the JWT header
        header = decode_jwt_header(token)
        logger.info(f"Decoded JWT header (unverified): {header}")

        # Step 2: Extract the Key ID ('kid') from header
        kid = header.get("kid")
        if not kid:
            logger.error("Token missing 'kid' in header.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid JWT: missing 'kid' in header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"Token 'kid' identified: {kid}")

        # Step 3: Retrieve the matching JWK (JSON Web Key) for the 'kid'
        jwk = await fetch_jwk_for_kid(kid)

        # Step 4: Convert the JWK to an RSA public key
        rsa_public_key = convert_jwk_to_rsa_public_key(jwk)

        # Step 5: Verify the token's signature, decode the payload and ensure that the audience is correct
        verified_payload = jwt.decode(
            token,
            rsa_public_key,
            algorithms=["RS256"],
            audience=AzureConfig.SERVER_CLIENT_ID
        )

        logger.info(f"Token signature successfully verified with public key (kid: {kid})")

        if "scp" in verified_payload:
            if isinstance(verified_payload["scp"], str):
                # Split the `scp` string into a list of scopes if necessary
                verified_payload["scp"] = verified_payload["scp"].split()
                logger.info(f"Parsed 'scp' claim into list: {verified_payload['scp']}")
            elif isinstance(verified_payload["scp"], list):
                logger.info("Token 'scp' claim is already a list.")
            else:
                logger.error(f"Unexpected 'scp' claim format: {type(verified_payload['scp'])}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid JWT: 'scp' claim format is incorrect",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return DecodedToken(**verified_payload)

    except ExpiredSignatureError:
        logger.error("Token has expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except MissingRequiredClaimError:
        logger.error("Invalid claims in token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        logger.error("Signature verification failed.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.exception("An unexpected error occurred while verifying the token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_jwt_header(token):
    header = token.split('.')[0]
    decoded_header = base64.urlsafe_b64decode(header + '==')
    return json.loads(decoded_header)


# Function to decode JWT payload/claims
def decode_jwt_payload(token):
    payload = token.split('.')[1]
    decoded_payload = base64.urlsafe_b64decode(payload + '==')
    return json.loads(decoded_payload)
