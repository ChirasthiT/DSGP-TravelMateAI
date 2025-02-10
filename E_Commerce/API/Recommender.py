import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet


class Recommender:
    def __init__(self, max_features=100, ngram_range=(1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.tfidf_vectorizer = None
        self.encoder = OneHotEncoder()
        self.budget_mapping = {"low": 1, "median": 2, "high": 3, "nan": 0}

    def load_data(self, collection):
        data = list(collection.find({}, {"_id": 0}))  # Exclude `_id`
        data = pd.DataFrame(data)
        data['District'] = data['District'].str.lower()
        data['Category'] = data['Category'].str.lower()
        data['Budget Level'] = data['Budget Level'].str.lower().map(self.budget_mapping)

        return data

    def preprocess_data(self, data):
        # One-hot encode District
        district_encoded = self.encoder.fit_transform(data[["District"]]).toarray()
        district_df = pd.DataFrame(district_encoded, columns=self.encoder.get_feature_names_out(["District"]))

        # Encode Category using TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(max_features=self.max_features, ngram_range=self.ngram_range)
        category_tfidf = self.tfidf_vectorizer.fit_transform(data["Category"])
        category_features = pd.DataFrame(category_tfidf.toarray(),
                                         columns=self.tfidf_vectorizer.get_feature_names_out())

        # Combine all features into one DataFrame
        feature_df = pd.concat([data[["Budget Level"]], district_df, category_features], axis=1)
        return data, feature_df

    def recommend(self, user_budget=None, user_district=None, user_category=None, data=None, feature_df=None, top_n=5):
        if user_district:
            user_district = user_district.lower()
        if user_category:
            user_category = user_category.lower()

        # Map user_budget to numeric value
        user_budget = self.budget_mapping.get(user_budget.lower(), 0) if user_budget else data["Budget Level"].mean()

        # Create user preference vector
        user_vector = pd.DataFrame([[user_budget] +
                                    [1 if col == f"District_{user_district}" else 0 for col in feature_df.columns[1:]]],
                                   columns=feature_df.columns)

        # Compute cosine similarity
        similarity_scores = cosine_similarity(user_vector, feature_df)[0]
        data["Similarity"] = similarity_scores

        # Apply filters
        recommendations = data.copy()
        if user_district:
            recommendations = recommendations[recommendations["District"] == user_district]
        if user_category:
            recommendations = recommendations[
                recommendations["Category"].str.contains(user_category, case=False, na=False)]

        recommendations = recommendations.sort_values(by="Similarity", ascending=False)
        return recommendations[
            ["Category", "Name", "Address", "District", "Budget Level", "Rating", "Similarity"]].head(top_n)


