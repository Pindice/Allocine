# Utiliser une image Python officielle
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel l'application sera accessible
EXPOSE 8501

# Commande pour exécuter l'application
CMD ["streamlit", "run", "main.py"]
