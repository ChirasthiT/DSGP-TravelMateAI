import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import re
import pickle
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk

# Ensure you have downloaded the necessary NLTK data files
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')


class ProductRecommender:
    def __init__(self, n_clusters=3, max_features=100, ngram_range=(1, 2)):
        self.n_clusters = n_clusters
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.kmeans = None
        self.tfidf_vectorizer = None
        self.scaler = None
        self.lemmatizer = WordNetLemmatizer()

    def load_data(self, filepath):
        data = pd.read_csv(filepath)
        data['Description'] = data['Description'].fillna("").str.lower()
        return data

    def preprocess_data(self, data):
        self.scaler = MinMaxScaler()
        data['Normalized Price'] = self.scaler.fit_transform(data[['Price']])
        return data

    def train_kmeans(self, data):
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        data['Price Cluster'] = self.kmeans.fit_predict(data[['Normalized Price']])
        return data

    def generate_tfidf(self, data):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=self.max_features, ngram_range=self.ngram_range)
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(data['Description'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=self.tfidf_vectorizer.get_feature_names_out())
        data = pd.concat([data, tfidf_df], axis=1)
        return data

    def infer_user_cluster(self, user_data):
        if isinstance(user_data, pd.DataFrame) and 'Price' in user_data.columns:
            avg_price = np.mean(user_data['Price'])
            normalized_data = self.scaler.transform([[avg_price]])
            user_cluster = self.kmeans.predict(normalized_data)[0]
        else:
            user_cluster = self.n_clusters // 2
        return user_cluster

    def recommend_products(self, data, user_cluster=None, keywords=None, top_n=5):
        if keywords is None:
            keywords = []

        if user_cluster is not None:
            cluster_products = data[data['Price Cluster'] == user_cluster].copy()
        else:
            cluster_products = data.copy()

        if keywords:
            # Create TF-IDF vector for the input keywords
            expanded_keywords = self.expand_keywords(keywords)
            keyword_vec = self.tfidf_vectorizer.transform([' '.join(expanded_keywords)])
            # Compute cosine similarities between keyword vector and product descriptions
            similarities = cosine_similarity(keyword_vec,
                                             cluster_products[self.tfidf_vectorizer.get_feature_names_out()])
            cluster_products['Keyword Match Score'] = similarities[0]
            recommendations = cluster_products.sort_values(by=['Keyword Match Score', 'Price'],
                                                           ascending=[False, True]).head(top_n)
        else:
            recommendations = cluster_products.sort_values(by='Price').head(top_n)

        return recommendations[['Product Name', 'Category', 'Price', 'Keyword Match Score', 'Description']]

    def extract_keywords(self, input_text):
        input_text = re.sub(r'[^a-z\s]', '', input_text.lower())
        stopwords = set(['the', 'a', 'an', 'and', 'in', 'on', 'at', 'to', 'of', 'for', 'during', 'is', 'was'])
        tokens = word_tokenize(input_text)
        keywords = [self.lemmatizer.lemmatize(word) for word in tokens if word not in stopwords]
        return list(keywords)

    def expand_keywords(self, keywords):
        expanded_keywords = []
        for keyword in keywords:
            expanded_keywords.append(keyword)
            for syn in wordnet.synsets(keyword):
                for lemma in syn.lemmas():
                    expanded_keywords.append(lemma.name().lower())
        return list(set(expanded_keywords))



# Example usage:
# recommender = ProductRecommender(n_clusters=3, max_features=100, ngram_range=(1, 2))
# data = recommender.load_data('products.csv')
# data = recommender.preprocess_data(data)
# data = recommender.train_kmeans(data)
# data = recommender.generate_tfidf(data)
# recommender.save_model('product_recommender_model.pkl')

# To load the model later:
# recommender.load_model('product_recommender_model.pkl')
# user_data = pd.DataFrame({'Price': [100, 200, 300]})
# user_cluster = recommender.infer_user_cluster(user_data)
# recommendations = recommender.recommend_products(data, user_cluster=user_cluster, keywords=['electric'], top_n=5)
# print(recommendations)