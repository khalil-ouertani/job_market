FROM python:3.9-slim

WORKDIR /app

# Copier les fichiers du répertoire actuel vers le conteneur
COPY ./vect_tfidf.py /app/tfidf_script.py
COPY ./vect_word2vec.py /app/word2vec_script.py
COPY ./create_ids.py /app/create_ids.py
COPY ./run_all.sh /app/run_all.sh

RUN pip install elasticsearch scikit-learn==1.3.2 gensim nltk passlib

# Télécharger les ressources NLTK nécessaires
RUN python -m nltk.downloader punkt stopwords punkt_tab

RUN chmod +x /app/run_all.sh

CMD ["bash", "/app/run_all.sh"]