from fastapi import APIRouter
from app.api.routes import signup, login, view_all_users, view_current_user, update_user_data, delete_data, logout

api_router = APIRouter()

api_router.include_router(signup.router)
api_router.include_router(login.router)
api_router.include_router(view_all_users.router)
api_router.include_router(view_current_user.router)
api_router.include_router(update_user_data.router)
api_router.include_router(delete_data.router)
api_router.include_router(logout.router)