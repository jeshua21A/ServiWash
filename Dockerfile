FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependencias del sistema necesarias para compilar o conectar drivers de MySQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python desde Backend/requirements.txt
COPY Backend/requirements.txt /app/Backend/requirements.txt
RUN pip install --no-cache-dir -r /app/Backend/requirements.txt

# Copiar todo el Backend (APIs + API Gateway + auth.py)
COPY Backend /app/Backend
# Copiar la carpeta compilada del Frontend (Web_App)
COPY Frontend/Web-App /app/Frontend/Web-App

WORKDIR /app/Backend

# Dar permiso de ejecución a start_apis.sh
RUN chmod +x /app/Backend/start_apis.sh

EXPOSE 8000

CMD ["bash", "/app/Backend/start_apis.sh"]