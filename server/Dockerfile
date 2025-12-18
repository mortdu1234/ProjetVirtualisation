FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le dossier shared (protocole commun)
COPY shared/ /app/shared/

# Copier les fichiers du serveur
COPY server/ /app/server/

# Définir le répertoire de travail sur server
WORKDIR /app/server

# Exposer le port du serveur
EXPOSE 5555

# Lancer le serveur
CMD ["python", "server.py"]