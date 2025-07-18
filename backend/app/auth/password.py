# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# async def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# async def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)


from passlib.context import CryptContext
from starlette.concurrency import run_in_threadpool

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await run_in_threadpool(pwd_context.verify, plain_password, hashed_password)

async def get_password_hash(password: str) -> str:
    return await run_in_threadpool(pwd_context.hash, password)

