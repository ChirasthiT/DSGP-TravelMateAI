from gensim.models import KeyedVectors
from gensim import downloader

# Load the Word2Vec model from gensim's pre-trained models
word_vectors = downloader.load("word2vec-google-news-300")

# Test similarity
similarity = word_vectors.similarity("waterproof", "water-resistant")
print(f"Similarity between 'waterproof' and 'water-resistant': {similarity}")




