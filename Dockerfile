FROM python:3.12.3-alpine3.19

WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# --no-cache-dir option is used to prevent pip from caching the packages, which reduces the image size
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use gunicorn for production deployment
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-5000} 'app:create_app()'"]


