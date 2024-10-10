'''
    Imported required libraries
    Added flask and celery on __init__ files so they will run before anything else
    also can br imported as package
'''

import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient
from .celery_task.celery_ import celery_init_app

# Added environment variable
load_dotenv()

# Created new flask app
app = Flask(__name__)

# Added info to celery
app.config.from_mapping(
    CELERY={
        "broker_url": "redis://localhost",
        "result_backend": "redis://localhost",
        "task_ignore_result": True,
    }
)
# Created celery app
celery_app = celery_init_app(app)

# Added flask secret key in env
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Added mongoclient 
client = MongoClient('localhost', 27017)

# Creating mongo database

db = client.sentiment_analysis_db

# Created mongo database collection
sentiment_analysis_db = db.sentiment_analysis
