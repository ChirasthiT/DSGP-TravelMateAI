import pandas as pd
import numpy as np
import re
import random
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity

class Recommender:
    def __init__(self, max_features=100, ngram_range=(1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.district_encoder = OneHotEncoder()  # Separate encoder for District
        self.source_encoder = OneHotEncoder()    # Separate encoder for Source
        self.budget_mapping = {"low": 1, "median": 2, "high": 3, "nan": 0}

    def load_data(self, collection):
        data = list(collection.find({}, {"_id": 0}))  # Exclude `_id`
        data = pd.DataFrame(data)
        data['District'] = data['District'].str.lower()
        data['Source'] = data['Source'].str.lower()
        data['Budget Level'] = data['Budget Level'].str.lower().map(self.budget_mapping)

        return data

    def preprocess_data(self, data):
        # One-hot encode District
        district_encoded = self.district_encoder.fit_transform(data[["District"]]).toarray()
        district_df = pd.DataFrame(district_encoded, columns=self.district_encoder.get_feature_names_out(["District"]))

        # One-hot encode Source (Accommodation/Restaurant)
        source_encoded = self.source_encoder.fit_transform(data[["Source"]]).toarray()
        source_df = pd.DataFrame(source_encoded, columns=self.source_encoder.get_feature_names_out(["Source"]))

        # Combine all features into one DataFrame
        feature_df = pd.concat([data[["Budget Level"]], district_df, source_df], axis=1)
        return data, feature_df

    def recommend(self, user_budget=None, user_district=None, user_category=None, data=None, feature_df=None, top_n=6):
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
            recommendations = recommendations[recommendations["Source"].str.contains(user_category, case=False, na=False)]
        recommendations = recommendations.sort_values(by="Similarity", ascending=False)
        top_n_recommendations = recommendations.head(top_n)
        r_recommendations = top_n_recommendations.sample(frac=1).reset_index(drop=True)

        return r_recommendations[["Source", "Name", "Address", "District", "Budget Level", "Rating", "Similarity", "Image"]].head(top_n)
