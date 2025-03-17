import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


class Recommender:
    def __init__(self,db):
        self.district_encoder = OneHotEncoder()
        self.source_encoder = OneHotEncoder()
        self.budget_mapping = {"low": 1, "median": 2, "high": 3}
        self.db = db

    def load_data(self, collection):
        data = pd.DataFrame(list(collection.find({}, {"_id": 0})))
        data["District"] = data["District"].str.lower()
        data["Source"] = data["Source"].str.lower()
        data["Budget Level"] = data["Budget Level"].str.lower().map(self.budget_mapping).fillna(0)
        return data

    def load_click_data(self):
        click_data = list(self.db["ECuser_clicks"].find({}, {"_id": 0}))
        df = pd.DataFrame(click_data)

        # Create a User-Item matrix
        user_item_matrix = df.pivot_table(index="user_email", columns="name", aggfunc="size", fill_value=0)
        return user_item_matrix

    def preprocess_data(self, data):
        district_encoded = self.district_encoder.fit_transform(data[["District"]]).toarray()
        source_encoded = self.source_encoder.fit_transform(data[["Source"]]).toarray()

        district_df = pd.DataFrame(district_encoded, columns=self.district_encoder.get_feature_names_out(["District"]))
        source_df = pd.DataFrame(source_encoded, columns=self.source_encoder.get_feature_names_out(["Source"]))

        return data, pd.concat([data[["Budget Level"]], district_df, source_df], axis=1)

    def recommend(self, user_budget, user_district, data, feature_df, top_n=20):
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

    def item_based_recommend(self, user_email, district, top_n=20):
        user_item_matrix = self.load_click_data()
        if user_item_matrix.empty or user_email not in user_item_matrix.index:
            return "Not enough interaction data for this user."

        item_similarity = cosine_similarity(user_item_matrix.T)  # Transpose to get item-item similarity
        item_sim_df = pd.DataFrame(item_similarity, index=user_item_matrix.columns, columns=user_item_matrix.columns)

        user_interactions = user_item_matrix.loc[user_email]
        interacted_items = user_interactions[user_interactions > 0].index.tolist()

        if not interacted_items:
            return "User has not interacted with any items."

        # Score items based on similarity to interacted items
        item_scores = {}
        for item in interacted_items:
            similar_items = item_sim_df[item].drop(index=interacted_items,
                                                   errors='ignore')  # Exclude already interacted items
            for similar_item, score in similar_items.items():
                item_scores[similar_item] = item_scores.get(similar_item, 0) + score

        item_scores_df = pd.DataFrame(item_scores.items(), columns=['Item', 'Score'])
        data = self.load_data(self.db["EC_Data"])  # Replace with the actual collection name
        item_district_mapping = data.set_index('Name')['District'].to_dict()

        item_scores_df["District"] = item_scores_df["Item"].map(item_district_mapping)
        filtered_recommendations = item_scores_df[item_scores_df["District"] == district.lower()]
        recommendations = filtered_recommendations.merge(
            data[["Source", "Name", "Address", "District", "Budget Level", "Rating", "Image"]],
            left_on='Item', right_on='Name', how='left'
        )

        recommendations = recommendations.drop(columns=["District_y"]).rename(columns={"District_x": "District"})
        recommendations = recommendations[
            ["Source", "Name", "Address", "District", "Budget Level", "Rating", "Score", "Image"]]

        return recommendations.sort_values(by="Score", ascending=False).head(top_n)


