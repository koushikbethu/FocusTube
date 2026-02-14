"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import jwt, JWTError
import httpx
from typing import Optional

from app.database import get_db
from app.config import get_settings
from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, TokenResponse, UserResponse, UserWithToken

router = APIRouter()
settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def create_access_token(user_id: str) -> TokenResponse:
    """Create JWT access token."""
    expires = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user_id,
        "exp": expires,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60
    )


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # Convert string to UUID
        import uuid as uuid_module
        user_uuid = uuid_module.UUID(user_id)
    except JWTError:
        raise credentials_exception
    except ValueError:
        # Invalid UUID format
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


@router.get("/google")
async def google_auth_redirect():
    """Redirect to Google OAuth consent screen."""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={settings.google_redirect_uri}&"
        "response_type=code&"
        "scope=openid%20email%20profile%20https://www.googleapis.com/auth/youtube.readonly&"
        "access_type=offline&"
        "prompt=consent"
    )
    return RedirectResponse(url=google_auth_url)


@router.get("/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback."""
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for tokens"
            )
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        
        # Get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info"
            )
        
        user_info = user_response.json()
    
    # Find or create user
    result = await db.execute(
        select(User).where(User.google_id == user_info["id"])
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        user = User(
            email=user_info["email"],
            google_id=user_info["id"],
            display_name=user_info.get("name"),
            avatar_url=user_info.get("picture"),
        )
        db.add(user)
        await db.flush()
    else:
        user.last_login = datetime.utcnow()
        user.avatar_url = user_info.get("picture")
    
    await db.commit()
    
    # Create JWT token
    token = create_access_token(str(user.id))
    
    # Redirect to frontend with token
    frontend_callback = f"{settings.frontend_url}/auth/callback?token={token.access_token}"
    return RedirectResponse(url=frontend_callback)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(user: User = Depends(get_current_user)):
    """Refresh access token."""
    return create_access_token(str(user.id))


@router.post("/logout")
async def logout():
    """Logout user (client should discard token)."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info."""
    return user


@router.get("/demo")
async def demo_login(db: AsyncSession = Depends(get_db)):
    """
    Demo login - creates/uses a test user without OAuth.
    For development and portfolio demos only.
    """
    demo_email = "demo@focustube.dev"
    
    # Find or create demo user
    result = await db.execute(
        select(User).where(User.email == demo_email)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        user = User(
            email=demo_email,
            google_id="demo-user-001",
            display_name="Demo User",
            avatar_url=None,
        )
        db.add(user)
        await db.flush()
    
    await db.commit()
    
    # Create JWT token
    token = create_access_token(str(user.id))
    
    # Redirect to frontend with token
    frontend_callback = f"{settings.frontend_url}/auth/callback?token={token.access_token}"
    return RedirectResponse(url=frontend_callback)
