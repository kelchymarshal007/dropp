import os
import time
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery('dropp_worker', broker=redis_url)
celery = app  # alias so `-A app.tasks.notifications` resolves

@app.task(name="send_email_notification", bind=True, max_retries=3)
def send_email_notification(self, user_id: str, title: str, body: str):
    try:
        print(f"[EMAIL MOCK] To User {user_id}: {title} - {body}", flush=True)
        time.sleep(1)
        return {"status": "sent"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)

@app.task(name="send_sms_notification", bind=True, max_retries=3)
def send_sms_notification(self, user_id: str, title: str, body: str):
    try:
        print(f"[SMS MOCK] To User {user_id}: {title} - {body}", flush=True)
        time.sleep(1)
        return {"status": "sent"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
