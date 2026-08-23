import uvicorn

from typing import Annotated
from bson import ObjectId
from datetime import datetime, timedelta, UTC

from fastapi import FastAPI, APIRouter, Form, HTTPException, Depends, Request, Response, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, add_pagination, paginate

from redis_fastapi import FastAPIRedis, cache, cache_evict, cache_put, default_key_builder

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from starlette.responses import JSONResponse

# Imports from other files.
from database.configurations import lifespan, db_client, user_db
from models.star_model import Star, example
from models.auth import Token, User, oauth2_scheme, authenticate_user, create_access_token, get_current_active_user
from schema.schemas import list_serializer



# Configure Fast API and Caching
router = APIRouter()
app = FastAPI(lifespan=lifespan,
              title='Stellar Objects API',
              description='Stellar Objects API',
              version='0.1.0',)

FastAPIRedis(app).lifespan().caching()
app.include_router(router)

# Pagination
add_pagination(app)

# Limiter
limiter = Limiter(key_func=get_remote_address,
                  headers_enabled=True)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,
                          _rate_limit_exceeded_handler)

# Root endpoint
@app.get('/', tags=['root'])
@limiter.limit('100/day; 5/minute')
async def get_root(request: Request,
                   response: Response,):
    return {'Welcome to the Stellar Objects API!'}

# JWT Token
@app.post("/token", tags=['Auth'])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await authenticate_user(user_db['collection'],
                                   form_data.username,
                                   form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

# Logged in user information
@app.get('/users/me', tags=['Auth'])
async def read_user_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user

# Show default star data
@app.get('/stars',
         tags=['stars'],
         dependencies=[Depends(cache(ttl=300,
                                     eviction_group='stars'))])
@limiter.limit('200/day; 20/hour')
async def get_stars(request: Request,
                    response: Response,
                    name: str | None = None,
                    constellation: str | None = None,
                    spectral_class: str | None = None,
                    evolutionary_stage: str | None = None,
                    category: str | None = None,
                    is_multi_star: bool | None = None,
                    has_planets: bool | None = None) -> Page[Star]:

    # MongoDB Collection
    star_collection = db_client['collection']

    # Filtering
    query = {}
    fields = {'name': name,
              'constellation': constellation,
              'spectral_class': spectral_class,
              'evolutionary_stage': evolutionary_stage,
              'category': category,
              'is_multi_star': is_multi_star,
              'has_planets': has_planets
              }

    for key, value in fields.items():
        if value is not None:
            query[key] = value

    cursor = star_collection.find(query)
    raw_data = await cursor.to_list(length=100)

    stars = list_serializer(raw_data)
    return paginate(stars)

# Get star by id
@app.get('/stars/{star_id}',
         tags=['stars'],
         dependencies=[Depends(cache(ttl=300,
                                     eviction_group='stars'))])
@limiter.limit('200/day; 20/hour')
async def get_star(request: Request,
                   response: Response,
                   star_id: str):

    # MongoDB Collection
    star_collection = db_client['collection']

    cursor = star_collection.find({'_id': ObjectId(star_id)})
    raw_data = await cursor.to_list(length=100)

    star = list_serializer(raw_data)
    if not star:
        raise HTTPException(status_code=404, detail='Star not found')
    return star

# Add a star
@app.post('/stars',
          tags=['stars'],
          dependencies=[Depends(cache_put(ttl=300,
                                          eviction_group='stars',
                                          key_builder=default_key_builder))])
@limiter.limit("5/minute")
async def add_star(request: Request,
                   response: Response,
                   star: Annotated[Star, Form(), Body(examples=example)],
                   token: Annotated[str, Depends(oauth2_scheme)]):

    # MongoDB Collection
    star_collection = db_client['collection']

    star_dict = star.model_dump()
    star_dict['created_at'] = datetime.now(tz=UTC)
    await star_collection.insert_one(star_dict)

    return JSONResponse(content={'message':'Star added successfully!',
                                 'status': '201',
                                 'token': token}, status_code=201)

# Update fields for a star
@app.put('/stars/{star_id}',
         tags=['stars'],
         dependencies=[Depends(cache_put(ttl=300,
                                         eviction_group='stars',
                                         key_builder=default_key_builder))])
@limiter.limit("5/minute")
async def update_star(request: Request,
                      star_id: str,
                      star: Annotated[Star, Form(), Body(examples=example)],
                      token: Annotated[str, Depends(oauth2_scheme)]):

    # MongoDB Collection
    star_collection = db_client['collection']

    star_dict = star.model_dump(exclude={'created_at'})
    star_dict['updated_at'] = datetime.now(tz=UTC)
    await star_collection.update_one({'_id': ObjectId(star_id)},{'$set': star_dict}, upsert=True)

    return JSONResponse(content={'message':'Star updated successfully!',
                                 'status': '200',
                                 'token': token}, status_code=200)

# Delete a star
@app.delete('/stars/{star_id}',
            tags=['stars'],
            dependencies=[Depends(cache_evict(eviction_group='stars',
                                                key_builder=default_key_builder))])
@limiter.limit("10/day")
async def delete_star(request: Request,
                      response: Response,
                      star_id: str,
                      token: Annotated[str, Depends(oauth2_scheme)]):
    # MongoDB Collection
    star_collection = db_client['collection']

    await star_collection.delete_one({'_id': ObjectId(star_id)})

    return JSONResponse(content={'message':'Star deleted successfully!',
                                 'status': '200',
                                 'token': token}, status_code=200)

# Run Uvicorn Server
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)