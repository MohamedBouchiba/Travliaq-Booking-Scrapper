FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pour la production, on lance l'API plutôt que les exemples
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
