web: gunicorn flaskr.app:app
worker: celery --app="tareas" --loglevel=info --pool=prefork --concurrency=20 worker 