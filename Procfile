web: gunicorn whatsapp_gpt_bot.wsgi:application --bind 0.0.0.0:8080
worker: celery -A whatsapp_gpt_bot worker --loglevel=info