# Utiliser l'image Python officielle
FROM python:3.12-slim

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances de compilation pour GDAL et outils de configuration
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    ca-certificates \
    curl \
    g++ \
    gcc \
    cmake \
    autoconf \
    automake \
    libtool \
    libproj-dev \
    libtiff-dev \
    libgeos-dev \
    libjson-c-dev \
    libjpeg-dev \
    libpng-dev \
    libsqlite3-dev \
    libcurl4-gnutls-dev \
    python3-dev \
    python3-pip \
    wget \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Télécharger et compiler GDAL 3.9.2 avec CMake
RUN curl -O http://download.osgeo.org/gdal/3.9.2/gdal-3.9.2.tar.gz && \
    tar -xvzf gdal-3.9.2.tar.gz && \
    cd gdal-3.9.2 && \
    cmake . && \
    make && \
    make install && \
    ldconfig

# Définir les variables d'environnement pour GDAL
ENV CPLUS_INCLUDE_PATH=/usr/local/include/gdal
ENV C_INCLUDE_PATH=/usr/local/include/gdal

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt /app/

# Installer les dépendances Python, y compris les bindings GDAL
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application dans le conteneur
COPY . /app/

# Exposer le port sur lequel l'application Django sera lancée
EXPOSE 8000

# Commande pour lancer l'application Django
CMD ["python", "start_daphne.py"]
