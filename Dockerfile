# Usamos la imagen oficial de Python 3.12 (versión ligera)
FROM python:3.12-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Evitamos que Python genere archivos .pyc y permitimos logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalamos las dependencias del sistema necesarias (si las hubiera)
# En este caso, limpiamos la caché para mantener la imagen pequeña
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero solo el archivo de requerimientos para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la aplicación
COPY . .

# Exponemos el puerto que definiste (8001)
EXPOSE 8001

# Comando para ejecutar la aplicación en producción
# Nota: Usamos 'run' en lugar de 'dev' para entornos Docker/Producción
CMD ["fastapi", "run", "main.py", "--port", "8001"]