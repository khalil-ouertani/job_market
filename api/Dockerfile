FROM python:3.9-slim

WORKDIR /app

COPY ./main.py /app/main.py

RUN pip install elasticsearch passlib fastapi uvicorn gensim scikit-learn==1.3.2 nltk numpy

RUN python -m nltk.downloader punkt stopwords punkt_tab

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]