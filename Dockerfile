# Usa una base Python leggera
FROM python:3.12-slim

# Imposta variabili d'ambiente sicure
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    unzip \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    libasound2 \
    libxshmfence1 \
    libxss1 \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crea la directory dell'app
WORKDIR /app

# Copia i file dell'app
COPY . .

# Installa i pacchetti Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Installa Playwright e i browser
RUN playwright install --with-deps

# Avvio dello script principale
CMD ["python", "main.py"]