# Usar una imagen base de Python 3.9
FROM python:3.9-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Instalar ffmpeg para el procesamiento de audio
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requisitos primero para aprovechar la caché de capas de Docker
COPY requirements.txt /app/

# Instalar las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos del proyecto en el directorio de trabajo
COPY . /app

# Exponer el puerto en el que la aplicación se ejecutará
EXPOSE 8080

# Configurar las variables de entorno necesarias
ENV PORT=8080

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
