import pickle
from datetime import datetime, timedelta
from typing import Optional

import redis
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    """
        Provides authentication and token management services.

        This class handles password hashing, token creation and decoding, and user retrieval based on tokens.

        Attributes:
            pwd_context: CryptContext instance for password hashing.
            SECRET_KEY: Secret key used for JWT encoding and decoding.
            ALGORITHM: Algorithm used for JWT encoding.
            cache: Redis cache for storing user data.
        """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    cache = redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD)

    def verify_password(self, plain_password, hashed_password):
        """
            Verifies if a plain text password matches the hashed password.

            Args:
                plain_password (str): The plain text password.
                hashed_password (str): The hashed password.

            Returns:
                bool: True if the password matches, False otherwise.
            """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
            Generates a hashed password from a plain text password.

            Args:
                password (str): The plain text password.

            Returns:
                str: The hashed password.
            """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
            Creates a JWT access token with optional expiration.

            Args:
                data (dict): The payload to include in the token.
                expires_delta (Optional[float]): Optional duration in seconds until token expiration.

            Returns:
                str: A JWT encoded access token.
            """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
            Creates a JWT refresh token with optional expiration.

            Args:
                data (dict): The payload to include in the token.
                expires_delta (Optional[float]): Optional duration in seconds until token expiration.

            Returns:
                str: A JWT encoded refresh token.
            """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
            Decodes a refresh token and returns the user's email.

            Args:
                refresh_token (str): The JWT refresh token.

            Returns:
                str: The email extracted from the token payload.

            Raises:
                HTTPException: If the token is invalid or has the wrong scope.
            """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
            Retrieves the current authenticated user based on the JWT token.

            Args:
                token (str): The JWT access token.
                db (AsyncSession): The database session.

            Returns:
                User: The authenticated user.

            Raises:
                HTTPException: If the token is invalid or the user is not found.
            """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)
        user = self.cache.get(user_hash)

        if user is None:
            print('User from db')
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print('User from cache')
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
            Creates a token for email verification purposes.

            Args:
                data (dict): The payload to include in the token.

            Returns:
                str: A JWT token for email verification.
            """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=2)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
            Decodes an email verification token to retrieve the user's email.

            Args:
                token (str): The JWT token for email verification.

            Returns:
                str: The email extracted from the token payload.

            Raises:
                HTTPException: If the token is invalid.
            """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
