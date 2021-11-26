web: gunicorn flaskr.app:app
worker: celery -A flaskr.tareas worker --pool=prefork --concurrency=5 --loglevel=info