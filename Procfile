web: gunicorn flaskr.app:app
worker: celery --app="tareas"  worker --pool=prefork --concurrency=20 --"tareas" 