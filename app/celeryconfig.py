from django.conf import settings

from env import Env

timezone = settings.TIME_ZONE
task_track_started = True
broker_url = Env("CELERY_BROKER_URL")
result_backend = Env("CELERY_RESULT_BACKEND")
cache_backend = "default"
delery_accept_content = ["application/json"]
task_serializer = "json"
result_serializer = "json"
worker_send_task_events = True
task_send_sent_event = True
broker_connection_retry_on_startup = True
broker_connection_retry = True
broker_connection_max_retries: int | None = None  # Retry forever
broker_connection_timeout = 30
broker_channel_error_retry = True


if settings.TEST:
    task_always_eager = True
    task_eager_propagates = True


imports = ("app.tasks",)
