from fastapi.security import HTTPBearer
from fastapi import HTTPException, Request, status
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_access_token


class AuthBearer(HTTPBearer):
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)
        
        if credentials is None:
            return None
        
        token = credentials.credentials
        token_data = decode_access_token(token)

        if not self.is_token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )   

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token"
            )
        
        if token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh tokens are not allowed here"
            )

        # Optional: Add JWT validation here
        # from app.auth.utils import verify_jwt
        # try:
        #     payload = verify_jwt(credentials.credentials)
        #     return payload  # or return credentials.credentials
        # except Exception:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid token"
        #     )
            
        # For now, just return the token string
        # return credentials.credentials
        return token_data
    
    def is_token_valid(self, token: str) -> bool:
        """
        Validate the JWT token.
        Args:
            token (str): The JWT token to validate.
        Returns:
            bool: True if the token is valid, False otherwise.
        """
        try:
            payload = decode_access_token(token)
            return True if payload else False
        except ValueError:
            return False