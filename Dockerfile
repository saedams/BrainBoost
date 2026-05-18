FROM python:3.12.3-alpine3.19

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

# Use gunicorn for production deployment
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
