# Utiliser une image Python de base
FROM python:3.11.10-slim

# Installer les dépendances systeme, y compris git et cron
RUN apt-get update && apt-get install -y git cron curl && rm -rf /var/lib/apt/lists/*

# Specifier le répertoire de travail dans le conteneur
WORKDIR /app

# Cloner le github
#RUN git clone https://github.com/gitreunion/datacup-challenge-data-lela.git .
COPY . .

# Installer les dépendances Python depuis requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Configurer un job cron pour rafraichir les donnes meteo une fois par mois
RUN echo "* * * 1 * /usr/local/bin/python /app/maj-meteo.py >> /var/log/cron.log 2>&1" > /etc/cron.d/cron-job

# Donner les permissions nécessaires au fichier cron
RUN chmod 0644 /etc/cron.d/cron-job

# Charger le job cron
RUN crontab /etc/cron.d/cron-job

# Creer un fichier de log pour cron
RUN touch /var/log/cron.log

# Configuration et verification exposition port 8080
EXPOSE 8080
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

# Lancer Streamlit et le service cron
CMD ["sh", "-c", "cron && streamlit run stream.py --server.port=8080 --server.address=0.0.0.0"]
