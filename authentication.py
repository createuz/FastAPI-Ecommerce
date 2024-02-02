import jwt
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
from fastapi import status
from emails import config_credentials
from models import User

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password):
    return pwd_context.hash(password)


async def very_token(token: str):
    try:
        payload = jwt.decode(token, config_credentials['SECRET'], algorithms='HS256')
        user = await User.get(id=payload.get('id'))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return user
