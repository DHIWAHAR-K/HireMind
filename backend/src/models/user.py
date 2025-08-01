from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from datetime import datetime
import bcrypt
import jwt
import os
from typing import Optional

# Import Base from database module to ensure consistency
from ..database import Base

class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    company_name = Column(String(200), nullable=True)
    job_title = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify the provided password against the stored hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.hashed_password.encode('utf-8')
        )
    
    def generate_token(self) -> str:
        """Generate JWT token for the user."""
        from datetime import datetime, timedelta
        
        payload = {
            'user_id': self.id,
            'email': self.email,
            'username': self.username,
            'exp': datetime.utcnow() + timedelta(hours=24)  # 24 hours
        }
        
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        # Ensure token is returned as string (newer PyJWT versions)
        if isinstance(token, bytes):
            return token.decode('utf-8')
        return token
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and verify JWT token."""
        try:
            secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def to_dict(self) -> dict:
        """Convert user object to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_picture': self.profile_picture,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'bio': self.bio
        }
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"