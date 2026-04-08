import os
import time
import random

from celery import Celery
from celery.result import AsyncResult

app = Celery(
    'random_number',
    broker='pyamqp://guest:guest@rabbitmq:5672//',       # rabbitmq service
    backend='redis://redis:6379/0'                       # redis service
)


@app.task
def random_number(max_value):
    time.sleep(5)
    return random.randint(0, 100)
