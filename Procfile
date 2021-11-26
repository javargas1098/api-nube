web: gunicorn flaskr.app:app
worker: celery --app=flaskr.tareas:app --loglevel=info --pool=prefork --concurrency=20 worker 