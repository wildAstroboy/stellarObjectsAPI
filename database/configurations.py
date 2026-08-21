import os

from fastapi import FastAPI
import pymongo
from dotenv import load_dotenv
from contextlib import asynccontextmanager


load_dotenv()

db_client = {}

# Create lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure the MongoDB Database and Collection
    mongodb_uri = os.getenv('MONGODB_URI')
    db_client['client'] = pymongo.AsyncMongoClient(mongodb_uri)
    db_client['db'] = db_client['client']['stellar_info']
    db_client['collection'] = db_client['db']['stars']

    # Ping the Cluster to confirm connection
    try:
        await db_client['client'].admin.command('ping')
        print('Successfully connected to MongoDB!')
    except Exception as e:
        print('Failed to connect to MongoDB!', e)

    yield

    await db_client['client'].close()
    print('Successfully disconnected from MongoDB!')