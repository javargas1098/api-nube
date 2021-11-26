web: gunicorn flaskr.app:app
worker: celery worker --app=flaskr.tareas --pool=prefork --concurrency=20 --loglevel=info