import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery('dropp_worker', broker=redis_url)

@app.task
def test_task():
    return "Worker is alive!"
