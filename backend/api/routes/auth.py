from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re

from src.auth import AuthService, get_current_user
from src.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

# Request models
class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 30:
            raise ValueError('Username must be less than 30 characters')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Name cannot be empty')
        if len(v) > 50:
            raise ValueError('Name must be less than 50 characters')
        return v.strip()

class UserLogin(BaseModel):
    email_or_username: str
    password: str

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    
    @validator('first_name', 'last_name', pre=True, always=True)
    def validate_names(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Name cannot be empty')
            if len(v) > 50:
                raise ValueError('Name must be less than 50 characters')
        return v

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

# Response models
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: Optional[str]
    company_name: Optional[str]
    job_title: Optional[str]
    bio: Optional[str]

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: UserResponse
    token: str

class MessageResponse(BaseModel):
    success: bool
    message: str

# Routes
@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserRegistration):
    """Register a new user account."""
    result = AuthService.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        company_name=user_data.company_name,
        job_title=user_data.job_title
    )
    
    if not result["success"]:
        if result["error_code"] == "EMAIL_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        elif result["error_code"] == "USERNAME_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return AuthResponse(**result)

@router.post("/login", response_model=AuthResponse)
async def login(login_data: UserLogin):
    """Authenticate user and return token."""
    result = AuthService.authenticate_user(
        email_or_username=login_data.email_or_username,
        password=login_data.password
    )
    
    if not result["success"]:
        if result["error_code"] in ["USER_NOT_FOUND", "INVALID_PASSWORD"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        elif result["error_code"] == "ACCOUNT_DEACTIVATED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return AuthResponse(**result)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(**current_user.to_dict())

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user profile."""
    result = AuthService.update_user_profile(
        user_id=current_user.id,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        company_name=profile_data.company_name,
        job_title=profile_data.job_title,
        bio=profile_data.bio
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return UserResponse(**result["user"])

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """Change user password."""
    result = AuthService.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    if not result["success"]:
        if result["error_code"] == "INVALID_CURRENT_PASSWORD":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return MessageResponse(**result)

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should remove token)."""
    return MessageResponse(
        success=True,
        message="Logged out successfully"
    )

@router.get("/validate-token")
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate if the current token is valid."""
    return {
        "success": True,
        "message": "Token is valid",
        "user_id": current_user.id,
        "username": current_user.username
    }