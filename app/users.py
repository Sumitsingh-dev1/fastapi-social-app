import uuid
import os
import logging
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from dotenv import load_dotenv
from app.db import User, get_user_db

# ------------------ ENV ------------------
load_dotenv()
SECRET = os.getenv("SECRET_KEY")

logging.basicConfig(level=logging.INFO)


# ------------------ USER MANAGER ------------------
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logging.info(f"User {user.id} registered")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        logging.info(f"User {user.id} forgot password")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        logging.info(f"Verification requested for {user.id}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


# ------------------ AUTH ------------------
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy():
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


# ------------------ USERS ------------------
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend]
)


current_active_user = fastapi_users.current_user(active=True)