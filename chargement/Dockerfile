FROM python:3.9-slim

RUN pip install elasticsearch

# Copier le script de chargement et les fichiers JSON dans le conteneur
COPY load_raw_to_ES.py /app/executor.py
COPY /data/franceTravail.json /app/franceTravail.json
COPY /data/indeed.json /app/indeed.json
COPY wait-for-it.sh /usr/bin/wait-for-it.sh
RUN chmod +x /usr/bin/wait-for-it.sh


WORKDIR /app

CMD ["python", "executor.py"]
