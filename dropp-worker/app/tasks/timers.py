import os
from datetime import datetime, timezone
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery('dropp_worker', broker=redis_url)
celery = app

app.conf.beat_schedule = {
    'auto-release-every-minute': {
        'task': 'auto_release_delivered',
        'schedule': 60.0,
    },
}

@app.task(name="auto_release_delivered")
def auto_release_delivered():
    print(f"[TIMER] Checking for delivered Dropps past auto-release time at {datetime.now(timezone.utc)}", flush=True)
