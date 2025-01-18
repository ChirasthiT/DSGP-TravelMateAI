import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import re
import pickle
from gensim.models import KeyedVectors
from gensim import downloader

class ProductRecommender:
    def __init__(self, n_clusters=3, max_features=100):
        self.n_clusters = n_clusters
        self.max_features = max_features
        self.kmeans = None
        self.tfidf_vectorizer = None
        self.scaler = None

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
        self.tfidf_vectorizer = TfidfVectorizer(max_features=self.max_features)
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(data['Description'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=self.tfidf_vectorizer.get_feature_names_out())
        data = pd.concat([data, tfidf_df], axis=1)
        return data

    def infer_user_cluster(self, user_data):
      """
      Infers the user's price cluster based on their interaction history.
      If no history is available, defaults to the "medium" cluster.
      """
      if isinstance(user_data, pd.DataFrame) and 'Price' in user_data:
          # If the Price column exists, calculate the average price
          avg_price = int(np.mean(user_data['Price']))

          # Prepare a DataFrame with the calculated average price and the correct column name
          user_data_df = pd.DataFrame([[avg_price]], columns=['Price'])

          # Normalize the price using the pre-fitted scaler
          normalized_data = self.scaler.transform(user_data_df[['Price']])

          # Add normalized price to the user data (as a new column)
          user_data_df['Normalized Price'] = normalized_data.flatten()

          # Predict the user's cluster using the trained KMeans model
          user_cluster = self.kmeans.predict(user_data_df[['Normalized Price']])[0]
      else:
          # Default to the "medium" cluster (i.e., cluster in the middle) if no price data
          user_cluster = self.n_clusters // 2

      return user_cluster

    def recommend_products(self, data, user_cluster=None, keywords=None, top_n=5):
        if keywords is None:
            keywords = []

        # Filter products by the user's cluster
        if user_cluster is not None:
            cluster_products = data[data['Price Cluster'] == user_cluster].copy()
        else:
            # Default to showing all clusters for new users
            cluster_products = data.copy()

        # Match keywords using TF-IDF features
        tfidf_columns = self.tfidf_vectorizer.get_feature_names_out()
        matching_scores = []
        for _, row in cluster_products.iterrows():
            product_keywords = " ".join(row[tfidf_columns].index[row[tfidf_columns] > 0])
            matched_keywords = [kw for kw in keywords if kw in product_keywords]
            matching_scores.append(len(matched_keywords))

        cluster_products['Keyword Match Score'] = matching_scores
        recommendations = cluster_products.sort_values(by=['Keyword Match Score', 'Price'],
                                                       ascending=[False, True]).head(top_n)
        return recommendations[['Product Name', 'Category', 'Price', 'Keyword Match Score']]

    def extract_keywords(self, input_text):
        input_text = re.sub(r'[^a-z\s]', '', input_text.lower())
        stopwords = set(['the', 'a', 'an', 'and', 'in', 'on', 'at', 'to', 'of', 'for', 'during', 'is', 'was'])
        keywords = [word for word in input_text.split() if word not in stopwords]

        # Now find synonyms for each keyword using Word2Vec
        enhanced_keywords = set(keywords)
        for keyword in keywords:
            try:
                # Find similar words for each keyword
                similar_words = self.word_vectors.most_similar(keyword, topn=3)  # Get top 3 similar words
                for word, similarity in similar_words:
                    enhanced_keywords.add(word)
            except KeyError:
                # If the word is not in the Word2Vec vocabulary, skip it
                pass

        return list(enhanced_keywords)

