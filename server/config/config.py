import os


class AzureConfig:
    TENANT_ID = os.getenv("HVALFANGST_TENANT_ID")
    SERVER_CLIENT_ID = os.getenv("HVALFANGST_API_SERVER_CLIENT_ID")
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    AUTHORIZATION_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"
    TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"
