FROM python:3.11-slim

WORKDIR /app

# Install chrome dependencies if needed for scraping, but starting simple
# If selenium/playwright is used, we might need a more complex base image or install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .

CMD ["python", "search_exemples.py"]
