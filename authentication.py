import jwt
from dotenv import dotenv_values
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
from fastapi import status
from models import User

config_credentials = dotenv_values('.env')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password):
    return pwd_context.hash(password)


async def very_token(token: str):
    try:
        payload = jwt.decode(jwt=token, key=config_credentials['SECRET'], algorithms=["HS256"])
        user = await User.get(id=payload.get('id'))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token', headers={'WWW-Authenticate': 'Bearer'})
    return user


async def verify_password(plan_password, hash_password):
    return pwd_context.verify(plan_password, hash_password)


async def authenticate_user(username, password):
    user = await User.get(username=username)
    if user and await verify_password(password, user.password):
        return user
    return False


async def token_generator(username: str, password: str):
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authorization': 'Bearer'}
        )
    token_data = {
        'id': user.id,
        'username': user.username
    }
    token = jwt.encode(payload=token_data, key=config_credentials['SECRET'], algorithm="HS256")
    return token
