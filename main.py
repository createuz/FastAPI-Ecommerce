from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import register_tortoise
from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save
from typing import Optional, Type
from emails import *
from authentication import *
from models import *

app = FastAPI()

templates = Jinja2Templates(directory='templates')

oath2_schema = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oath2_schema)):
    try:
        payload = jwt.decode(token, config_credentials['SECRET'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authorization': 'Bearer'}
        )
    return user


@app.post('/user/me')
async def user_login(user: user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(owner=user)
    return {
        'status': 'ok',
        'data': {
            'username': user.username,
            'verified': user.is_verified,
            'joined_date': user.join_date.strftme('%b %d %Y')
        }
    }


@app.post('/token')
async def generate_token(request_from: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_from.username, request_from.password)
    return {'access_token': token, 'token_type': 'bearer'}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@post_save(User)
async def create_business(sender: 'Type[User]', instance: User, created: bool,
                          using_db: 'Optional[BaseDBAsyncClient]', update_fields: List[str]) -> None:
    if created:
        business_obj = await Business.create(business_name=instance.username, owner=instance)
        await business_pydantic.from_tortoise_orm(business_obj)
        await send_email([instance.email], instance)


@app.post('/registration')
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info['password'] = get_hashed_password(user_info['password'])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {'status': 'ok', 'data': f'Hello {new_user.username}, thanks for choosing our services. '
                                    f'Please check your email inbox and click on the link to confirm your registration.'}


@app.get('/verification', response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await very_token(token)
    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse('verification.html', {'request': request, 'username': user.username})
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Invalid token or expired token',
                        headers={'WWW-Authenticate': 'Bearer'})


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True
)
