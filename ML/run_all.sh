#!/bin/bash

python tfidf_script.py &

python word2vec_script.py &

python create_ids.py &

wait