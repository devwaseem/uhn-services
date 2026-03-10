# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html#configuration-file
# https://docs.gunicorn.org/en/stable/settings.html

import multiprocessing
import os

bind = "0.0.0.0:3000"
# Concerning `workers` setting see:
# https://github.com/wemake-services/wemake-django-template/issues/1022

workers = os.environ.get(
    "GUNICORN_WORKERS",
    multiprocessing.cpu_count() * 2 + 1,
)
worker_class = os.environ.get(
    "GUNICORN_WORKER_CLASS",
    "sync",
)

threads = os.environ.get(
    "GUNICORN_THREADS",
    1,
)
worker_connections = os.environ.get(
    "GUNICORN_WORKER_CONNECTIONS",
    1000,
)

max_requests = os.environ.get(
    "GUNICORN_MAX_REQUESTS",
    2000,
)
max_requests_jitter = os.environ.get(
    "GUNICORN_REQUESTS_JITTER",
    400,
)

timeout = os.environ.get(
    "GUNICORN_TIMEOUT",
    90,
)

accesslog = "-"
errorlog = "-"
chdir = os.environ["APP_HOME"]
worker_tmp_dir = "/dev/shm"
