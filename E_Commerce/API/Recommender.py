import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity


class Recommender:
    def __init__(self):
        self.district_encoder = OneHotEncoder()
        self.source_encoder = OneHotEncoder()
        self.budget_mapping = {"low": 1, "median": 2, "high": 3}

    def load_data(self, collection):
        data = pd.DataFrame(list(collection.find({}, {"_id": 0})))
        data["District"] = data["District"].str.lower()
        data["Source"] = data["Source"].str.lower()
        data["Budget Level"] = data["Budget Level"].str.lower().map(self.budget_mapping).fillna(0)
        return data

    def preprocess_data(self, data):
        district_encoded = self.district_encoder.fit_transform(data[["District"]]).toarray()
        source_encoded = self.source_encoder.fit_transform(data[["Source"]]).toarray()

        district_df = pd.DataFrame(district_encoded, columns=self.district_encoder.get_feature_names_out(["District"]))
        source_df = pd.DataFrame(source_encoded, columns=self.source_encoder.get_feature_names_out(["Source"]))

        return data, pd.concat([data[["Budget Level"]], district_df, source_df], axis=1)

    def recommend(self, user_budget, user_district, data, feature_df, top_n=15):
        user_district = user_district.lower() if user_district else None
        user_budget = self.budget_mapping.get(user_budget.lower(), data["Budget Level"].mean())

        user_vector = pd.DataFrame(
            [[user_budget] + [1 if col == f"District_{user_district}" else 0 for col in feature_df.columns[1:]]],
            columns=feature_df.columns)

        data["Similarity"] = cosine_similarity(user_vector, feature_df)[0]
        recommendations = data if not user_district else data[data["District"] == user_district]

        return recommendations.sort_values(by="Similarity", ascending=False)[
            ["Source", "Name", "Address", "District", "Budget Level", "Rating", "Similarity", "Image"]
        ].head(top_n)
