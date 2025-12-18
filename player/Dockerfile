FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le dossier shared (protocole commun)
COPY shared/ /app/shared/

# Copier les fichiers du joueur
COPY player/ /app/player/

# Définir le répertoire de travail sur player
WORKDIR /app/player

# Lancer le client joueur
CMD ["python", "player.py"]