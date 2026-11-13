import os
import subprocess
import uuid
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery('dropp_worker', broker=redis_url)
celery = app

@app.task(name="process_video")
def process_video(post_id: str, input_path: str, output_dir: str = "/tmp/media"):
    print(f"[Media] Processing video for Post: {post_id}", flush=True)
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    command = [
        "ffmpeg", "-i", input_path, "-t", "12",
        "-vf", "scale=-2:720", "-c:v", "libx264",
        "-crf", "28", "-preset", "fast", "-y", output_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[Media] Compressed: {output_filename}", flush=True)
        return {"status": "ok", "file": output_filename}
    except subprocess.CalledProcessError as e:
        print(f"[Media] FFmpeg failed: {e.stderr.decode()}", flush=True)
        return {"status": "error"}
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
