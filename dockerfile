FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collecte des fichiers statiques uniquement en production
ARG DJANGO_ENV=dev
ENV DJANGO_ENV=${DJANGO_ENV}

# Copie du script
COPY entrypoint.sh /app/entrypoint.sh

# Expose le port
EXPOSE 8000

# Utilise le script comme commande de lancement
CMD ["/app/entrypoint.sh"]
