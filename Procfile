web: gunicorn config.wsgi:application
worker: celery worker --app=supplies_platform.taskapp --loglevel=info
