from client.logger import logger

# Global variable to hold the access token
ACCESS_TOKEN = None


def store_token(access_token: str):
    global ACCESS_TOKEN
    ACCESS_TOKEN = access_token
    logger.info(f"Access token successfully stored: {ACCESS_TOKEN}")


def get_stored_token():
    return ACCESS_TOKEN
