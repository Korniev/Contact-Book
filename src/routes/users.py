import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    Query,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schema.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(cloud_name=config.CLD_NAME, api_key=config.CLD_API_KEY, api_secret=config.CLD_API_SECRET, secure=True)


@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))], )
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
        Retrieves the current user's details.

        This endpoint is rate-limited to prevent abuse.

        Args:
            user (User): The current authenticated user, injected by the authentication service.

        Returns:
            UserResponse: The current user's details.

        Rate Limit:
            1 request per 20 seconds.
        """
    return user


@router.patch("/avatar", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))], )
async def get_current_user(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
        Updates the current user's avatar.

        The new avatar is uploaded to Cloudinary and the URL is updated in the user's profile.

        Args:
            file (UploadFile): The image file to be uploaded as the new avatar.
            user (User): The current authenticated user, injected by the authentication service.
            db (AsyncSession): The database session, injected by FastAPI.

        Returns:
            UserResponse: The user's updated details with the new avatar URL.

        Notes:
            - This endpoint is also rate-limited.
            - The user's data is cached with Redis after the update.

        Rate Limit:
            1 request per 20 seconds.
        """
    public_id = f"Korniev/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
