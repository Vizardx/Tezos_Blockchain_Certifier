# Usar una imagen base de Python en Ubuntu
FROM python:3.9-slim-buster

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    pkg-config \
    build-essential \
    libsodium-dev \
    libsecp256k1-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requisitos y el script de Python
COPY requirements.txt requirements.txt
RUN apt-get update -y && apt-get install -y iputils-ping \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*
COPY register_transaction_dyn_v3.py register_transaction_dyn_v3.py
COPY .env .env

# Crear la carpeta para los archivos de verificación
RUN mkdir -p /app/Verificacion_transaccional

# Comando para ejecutar el script
CMD ["python", "register_transaction_dyn_v2.py"]
