'''
    Imported required libraries
    Added flask and celery on __init__ files so they will run before anything else
    also can br imported as package
'''

import os
from flask import Flask
from dotenv import load_dotenv
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

# added flask secret key in env
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


