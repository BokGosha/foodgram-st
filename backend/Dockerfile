FROM python:3.10

WORKDIR /app

COPY requirements.txt .

COPY data/ingredients.json .

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["sh", "-c", "python manage.py migrate && \
                    python manage.py load_ingredients ./data/ingredients.json && \
                    python manage.py collectstatic --noinput && \
                    cp -r /app/collected_static/. /backend_static/static/ && \
                    gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"]
