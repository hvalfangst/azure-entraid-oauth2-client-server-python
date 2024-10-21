from typing import Optional, List

from pydantic import BaseModel


class DecodedToken(BaseModel):
    aud: str  # Audience
    iss: str  # Issuer
    iat: int  # Issued at (UNIX timestamp)
    nbf: int  # Not before (UNIX timestamp)
    exp: int  # Expiration (UNIX timestamp)
    aio: Optional[str] = None  # Authentication info (optional)
    azp: Optional[str] = None  # Authorized party (optional)
    azpacr: Optional[str] = None  # Additional auth context (optional)
    oid: str  # Object ID (user or service principal ID)
    rh: Optional[str] = None  # Refresh token claim (optional)
    sub: str  # Subject (identifier for the principal)
    tid: str  # Tenant ID
    uti: Optional[str] = None  # Unique token ID (optional)
    ver: str  # Token version
    roles: Optional[List[str]] = None  # Optional list of roles
    scope: Optional[str] = None  # Space-separated scopes string (common for OAuth 2.0)
    scp: Optional[List[str]] = None  # List of scopes, often used instead of `scope`

    def get_scopes(self) -> List[str]:
        """
        Returns a list of scopes, whether they are in `scope` (string) or `scp` (list) format.
        """
        if self.scp:
            return self.scp
        elif self.scope:
            return self.scope.split()
        return []
