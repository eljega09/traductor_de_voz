# Utiliza una imagen base oficial de Python como punto de partida
FROM python:3.8-slim

# Configura el entorno para que los mensajes de log y salida sean enviados directamente a la terminal sin ser bufferizados
ENV PYTHONUNBUFFERED True

# Instala dependencias del sistema para `ffmpeg`
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo para tu aplicación
WORKDIR /app

# Copia el archivo de requisitos y lo instala usando pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código fuente de la aplicación al directorio de trabajo
COPY . .

# Indica el comando para iniciar tu aplicación
CMD ["python", "app.py"]
