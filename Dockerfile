# Usamos la imagen oficial de Python 3.12 (versión ligera)
FROM python:3.12-slim

# Evitamos que Python genere archivos .pyc y permitimos logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos dependencias del sistema, librerías de desarrollo + Chrome (Todo en una capa)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    wget \
    curl \
    gnupg \
    unzip \
    git \
    libcairo2-dev \
    libgdal-dev \
    build-essential \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Variables de entorno para que los paquetes de Python encuentren GDAL durante la instalación
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copiamos requirements primero para aprovechar la caché de capas de Docker
COPY requirements.txt .

# Instalamos dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Verificación opcional de Chrome
RUN google-chrome --version

# Copiamos el resto del proyecto
COPY . .

# Compilamos los archivos de Cython (.pyx -> .so de Linux)
RUN python setup.py build_ext --inplace

# Puerto expuesto
EXPOSE 8001

# Ejecutamos FastAPI
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8001"]