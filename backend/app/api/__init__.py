from fastapi import APIRouter
from app.api.endpoints import signup_user, login_user, view_all_users, view_current_user, update_user_data, delete_user_data, logout_user

api_router = APIRouter()

api_router.include_router(signup_user.router)
api_router.include_router(login_user.router)
api_router.include_router(view_all_users.router)
api_router.include_router(view_current_user.router)
api_router.include_router(update_user_data.router)
api_router.include_router(delete_user_data.router)
api_router.include_router(logout_user.router)