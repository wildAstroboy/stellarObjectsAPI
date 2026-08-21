from typing import Annotated

import uvicorn
from fastapi import FastAPI, APIRouter, Form, HTTPException, Depends, Request, Response
from redis_fastapi import FastAPIRedis, cache, cache_evict, cache_put, default_key_builder
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from database.configurations import lifespan, db_client
from models.stars_model import Star
from schema.schemas import list_serializer
from bson import ObjectId
from datetime import datetime, UTC


# Configure Fast API and Caching
router = APIRouter()
app = FastAPI(lifespan=lifespan,
              title='Stellar Objects API',
              description='Stellar Objects API',
              version='0.1.0',)

FastAPIRedis(app).lifespan().caching()
app.include_router(router)

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
                    type: str | None = None,
                    category: str | None = None,):

    # MongoDB Collection
    star_collection = db_client['collection']

    query = {}
    fields = {'name': name,
              'constellation': constellation,
              'spectral_class': spectral_class,
              'type': type,
              'category': category
              }

    for key, value in fields.items():
        if value is not None:
            query[key] = value

    cursor = star_collection.find(query)
    raw_data = await cursor.to_list(length=100)

    stars = list_serializer(raw_data)
    return stars

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

@app.post('/stars',
          tags=['stars'],
          dependencies=[Depends(cache_put(ttl=300,
                                          eviction_group='stars',
                                          key_builder=default_key_builder))])
@limiter.limit("5/minute")
async def add_star(request: Request,
                   response: Response,
                   star: Annotated[Star, Form()]):

    # MongoDB Collection
    star_collection = db_client['collection']

    star_dict = star.model_dump()
    star_dict['created_at'] = datetime.now(tz=UTC)
    await star_collection.insert_one(star_dict)

    return JSONResponse(content={'message':'Star added successfully!',
                                 'status': '201'}, status_code=201)

@app.put('/stars/{star_id}',
         tags=['stars'],
         dependencies=[Depends(cache_put(ttl=300,
                                         eviction_group='stars',
                                         key_builder=default_key_builder))])
@limiter.limit("5/minute")
async def update_star(request: Request,
                      star_id: str,
                      star: Annotated[Star, Form()]):

    # MongoDB Collection
    star_collection = db_client['collection']

    star_dict = star.model_dump(exclude={'created_at'})
    star_dict['updated_at'] = datetime.now(tz=UTC)
    await star_collection.update_one({'_id': ObjectId(star_id)},{'$set': star_dict}, upsert=True)

    return JSONResponse(content={'message':'Star updated successfully!',
                                 'status': '200'}, status_code=200)

@app.delete('/stars/{star_id}',
            tags=['stars'],
            dependencies=[Depends(cache_evict(eviction_group='stars',
                                                key_builder=default_key_builder))])
@limiter.limit("10/day")
async def delete_star(request: Request,
                      response: Response,
                      star_id: str):
    # MongoDB Collection
    star_collection = db_client['collection']

    await star_collection.delete_one({'_id': ObjectId(star_id)})

    return JSONResponse(content={'message':'Star deleted successfully!',
                                 'status': '200'}, status_code=200)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)