release: python manage.py migrate
web: python manage.py collectstatic --noinput; uvicorn op_trans.asgi:application --host 0.0.0.0 --port $PORT --workers $WEB_CONCURRENCY