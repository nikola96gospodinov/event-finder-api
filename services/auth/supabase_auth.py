from typing import Any, Dict, Optional, cast

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

from core.logging_config import get_logger
from core.supabase_client import supabase_base
from models.user_profile_model import UserProfile
from utils.user_profile_utils import convert_from_supabase_user_to_user_profile

logger = get_logger(__name__)

security = HTTPBearer()


class SupabaseAuthService:
    def __init__(self):
        # The base client is already initialized in supabase_base
        pass

    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client from the base class"""
        return supabase_base.client

    async def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Supabase token"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None

        try:
            # Verify the token and get user info
            user_response = self.client.auth.get_user(token)
            if user_response and user_response.user:
                return user_response.user.model_dump()
            return None
        except Exception as e:
            logger.error(f"Error getting user from token: {e}")
            return None

    async def get_raw_profile_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get raw profile data from Supabase database"""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None

        try:
            response = (
                self.client.table("profiles")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return cast(Dict[str, Any], response.data[0])
            else:
                logger.error(f"No profile found for user_id: {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None


auth_service = SupabaseAuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[Dict[str, Any]]:
    """Dependency to get current user from bearer token"""
    token = credentials.credentials
    user = await auth_service.get_user_from_token(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_profile(
    user: Dict[str, Any] = Depends(get_current_user)
) -> UserProfile | None:
    """Dependency to get current user's profile"""
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    profile_data = await auth_service.get_raw_profile_data(user_id)
    if not profile_data:
        return None

    user_profile = convert_from_supabase_user_to_user_profile(profile_data, user)

    if not user_profile:
        raise HTTPException(
            status_code=400,
            detail="User profile not found. Please complete your profile setup first.",
        )

    return user_profile
