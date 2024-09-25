python manage.py makemigrations --no-input
python manage.py migrate --no-input
gunicorn --bind 0:8000 shades_of_flavor.wsgi