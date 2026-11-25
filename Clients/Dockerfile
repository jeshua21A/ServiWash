FROM python:3.14.10-slim-trixie

# Salida sin buffer y sin archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias primero para aprovechar la cache de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codigo del servicio (el .env no se copia: se inyectan variables en ejecucion)
COPY app ./app
COPY run.py ./run.py

# Ejecutar sin privilegios
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

# run.py escucha en 127.0.0.1, por eso se arranca la app publicada en 0.0.0.0
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5001"]
