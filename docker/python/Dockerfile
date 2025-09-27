FROM python:3.12-slim

# Actualiza e instala paquetes necesarios
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    libpq-dev \
    && apt-get clean

WORKDIR /usr/src/app
 
COPY requirements.txt .    
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip
CMD ["tail", "-f", "/dev/null"]