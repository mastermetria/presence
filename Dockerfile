# Étape 1 : Base image avec Python
FROM python:3.12-slim

# Étape 2 : Installer Chrome et ses dépendances
RUN apt-get update && apt-get install -y \
    lftp \
    wget \
    curl \
    gnupg \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Ajouter le repo Chrome et installer Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

    
# Étape 4 : Installer Python et Gunicorn
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : Copier le code de l'application
COPY app /app

# Étape 6 : Exposer le port et définir la commande de lancement
EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]