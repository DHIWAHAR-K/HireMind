from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from ..models.user import User

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthMiddleware:
    """Authentication middleware for FastAPI."""
    
    @staticmethod
    def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """Extract token from Authorization header."""
        return credentials.credentials
    
    @staticmethod
    def get_current_user(token: str = Depends(get_token_from_header)) -> User:
        """Get current authenticated user from token."""
        user = AuthService.get_user_by_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    @staticmethod
    def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
        """Get current active user."""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user

def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract token from Authorization header."""
    return credentials.credentials

def get_current_user(token: str = Depends(get_token_from_header)) -> User:
    """Get current authenticated user from token."""
    from .auth_service import AuthService
    
    user = AuthService.get_user_by_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    try:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user
    except Exception as e:
        # Handle detached instance error by re-fetching user
        from .auth_service import AuthService
        logger.warning(f"User instance detached, re-fetching: {e}")
        user = AuthService.get_user_by_id(current_user.id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user

# Optional authentication (doesn't raise exception if no token)
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        from .auth_service import AuthService
        user = AuthService.get_user_by_token(credentials.credentials)
        return user if user and user.is_active else None
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None