from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from ..models.user import User
from ..database import get_db_session

logger = logging.getLogger(__name__)

class AuthService:
    """Service class for handling authentication operations."""
    
    @staticmethod
    def create_user(
        email: str,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user account."""
        try:
            with get_db_session() as db:
                # Check if user already exists
                existing_user = db.query(User).filter(
                    (User.email == email) | (User.username == username)
                ).first()
                
                if existing_user:
                    if existing_user.email == email:
                        return {
                            "success": False,
                            "error": "Email already registered",
                            "error_code": "EMAIL_EXISTS"
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Username already taken",
                            "error_code": "USERNAME_EXISTS"
                        }
                
                # Create new user
                new_user = User(
                    email=email,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    company_name=company_name,
                    job_title=job_title
                )
                
                # Set password (will be hashed automatically)
                new_user.set_password(password)
                
                # Add to database
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                logger.info(f"New user created: {username} ({email})")
                
                # Generate token
                token = new_user.generate_token()
                
                return {
                    "success": True,
                    "message": "Account created successfully",
                    "user": new_user.to_dict(),
                    "token": token
                }
                
        except IntegrityError as e:
            logger.error(f"Database integrity error during user creation: {e}")
            return {
                "success": False,
                "error": "User already exists",
                "error_code": "INTEGRITY_ERROR"
            }
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {
                "success": False,
                "error": "Failed to create account",
                "error_code": "CREATION_ERROR"
            }
    
    @staticmethod
    def authenticate_user(email_or_username: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email/username and password."""
        try:
            with get_db_session() as db:
                # Find user by email or username
                user = db.query(User).filter(
                    (User.email == email_or_username) | (User.username == email_or_username)
                ).first()
                
                if not user:
                    return {
                        "success": False,
                        "error": "Invalid credentials",
                        "error_code": "USER_NOT_FOUND"
                    }
                
                if not user.is_active:
                    return {
                        "success": False,
                        "error": "Account is deactivated",
                        "error_code": "ACCOUNT_DEACTIVATED"
                    }
                
                # Verify password
                if not user.verify_password(password):
                    return {
                        "success": False,
                        "error": "Invalid credentials",
                        "error_code": "INVALID_PASSWORD"
                    }
                
                # Update last login
                user.last_login = datetime.utcnow()
                db.commit()
                
                # Generate token
                token = user.generate_token()
                
                logger.info(f"User authenticated: {user.username}")
                
                return {
                    "success": True,
                    "message": "Login successful",
                    "user": user.to_dict(),
                    "token": token
                }
                
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {
                "success": False,
                "error": "Authentication failed",
                "error_code": "AUTH_ERROR"
            }
    
    @staticmethod
    def get_user_by_token(token: str) -> Optional[User]:
        """Get user by JWT token."""
        try:
            payload = User.decode_token(token)
            if not payload:
                return None
            
            with get_db_session() as db:
                user = db.query(User).filter(User.id == payload['user_id']).first()
                if user and user.is_active:
                    # Expunge the user from the session so it can be used outside the session
                    db.expunge(user)
                    return user
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by token: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    # Expunge the user from the session so it can be used outside the session
                    db.expunge(user)
                return user
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def update_user_profile(
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
        bio: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user profile information."""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return {
                        "success": False,
                        "error": "User not found",
                        "error_code": "USER_NOT_FOUND"
                    }
                
                # Update fields if provided
                if first_name is not None:
                    user.first_name = first_name
                if last_name is not None:
                    user.last_name = last_name
                if company_name is not None:
                    user.company_name = company_name
                if job_title is not None:
                    user.job_title = job_title
                if bio is not None:
                    user.bio = bio
                
                user.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(user)
                
                logger.info(f"User profile updated: {user.username}")
                
                return {
                    "success": True,
                    "message": "Profile updated successfully",
                    "user": user.to_dict()
                }
                
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return {
                "success": False,
                "error": "Failed to update profile",
                "error_code": "UPDATE_ERROR"
            }
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password."""
        try:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return {
                        "success": False,
                        "error": "User not found",
                        "error_code": "USER_NOT_FOUND"
                    }
                
                # Verify current password
                if not user.verify_password(current_password):
                    return {
                        "success": False,
                        "error": "Current password is incorrect",
                        "error_code": "INVALID_CURRENT_PASSWORD"
                    }
                
                # Set new password
                user.set_password(new_password)
                user.updated_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Password changed for user: {user.username}")
                
                return {
                    "success": True,
                    "message": "Password changed successfully"
                }
                
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return {
                "success": False,
                "error": "Failed to change password",
                "error_code": "PASSWORD_CHANGE_ERROR"
            }