from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import File, UploadFile
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import register_tortoise
from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save
from typing import Optional, Type
from emails import *
from authentication import *
from models import *

app = FastAPI()

app.mount("/static", StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

oath2_schema = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oath2_schema)):
    try:
        payload = jwt.decode(jwt=token, key=config_credentials['SECRET'], algorithms=["HS256"])
        user = await User.get(id=payload.get('id'))
    except Exception:
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


@app.post('/uploadfile/profile')
async def create_upload_file(file: UploadFile = File(...),
                             user: user_pydantic = Depends()):
    FILEPATH = 'C:/Users/creat/OneDrive/Desktop/Projects/FastAPIEcommerce/static/images'
    filename = file.filename
    extension = filename.split('.')[1]
    if extension not in ['png', 'jpg']:
        return {'static': 'error', 'detail': 'File extension not allowed'}
    token_name = secrets.token_hex(10) + '.' + extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    with open(generated_name, 'wb') as file:
        file.write(file_content)
    img = Image.open(generated_name)
    img = img.resize(size=(200, 200))
    img.save(generated_name)
    file.close()

    business = await Business.get(owner=user)
    owner = await business.owner
    if owner == user:
        business.logo = token_name
        await business.save()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated to perform this action',
            headers={'WWW-Authenticate': 'Bearer'})
    file_url = 'localhost:8000' + generated_name[1:]
    return {'status': 'ok', 'filename': file_url}


@app.post('/uploadfile/product/{id}')
async def create_upload_file(id: int, file: UploadFile = File(...),
                             user: user_pydantic = Depends()):
    FILEPATH = 'C:/Users/creat/OneDrive/Desktop/Projects/FastAPIEcommerce/static/images'
    filename = file.filename
    extension = filename.split('.')[1]
    if extension not in ['png', 'jpg']:
        return {'static': 'error', 'detail': 'File extension not allowed'}
    token_name = secrets.token_hex(10) + '.' + extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    with open(generated_name, 'wb') as file:
        file.write(file_content)
    img = Image.open(generated_name)
    img = img.resize(size=(200, 200))
    img.save(generated_name)
    file.close()

    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner

    if owner == user:
        product.product_image = token_name
        await product.save()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated to perform this action',
            headers={'WWW-Authenticate': 'Bearer'})
    file_url = 'localhost:8000' + generated_name[1:]
    return {'status': 'ok', 'filename': file_url}


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True
)
