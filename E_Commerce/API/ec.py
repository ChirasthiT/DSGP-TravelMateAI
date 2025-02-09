from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
from urllib.parse import quote
import os
from Recommender import Recommender
from Product import Product
from flask_pymongo import PyMongo
from pydantic import BaseModel
import pandas as pd

app = Flask(__name__)
CORS(app)
# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/Products_info?retryWrites=true&w=majority&appName=DSGP'
db = PyMongo(app)

# Initialize the ProductRecommender
recommender = ProductRecommender(n_clusters=3, max_features=100)

# Preprocessed dataset
data = None  # Initialize globally to be set during startup

# Request models
class UserInteractionData(BaseModel):
    prices: list[float]  # List of past purchase prices

class RecommendationRequest(BaseModel):
    user_interaction_data: UserInteractionData = None
    keywords: str = None  # Keywords input by the user

def load_dataset():
    """Load and preprocess the dataset on application startup."""
    global data
    try:
        data = recommender.load_data("product_dataset.csv")
        data = recommender.preprocess_data(data)
        data = recommender.train_kmeans(data)
        data = recommender.generate_tfidf(data)
        print("Dataset successfully loaded and preprocessed.")
    except FileNotFoundError:
        print("Dataset file not found. Please ensure 'product_dataset.csv' is available.")
        raise RuntimeError("Dataset file missing, cannot start the API.")

# Home Route
@app.route('/EC.html')
def home():
    return render_template('EC.html')

# Recommend Route (GET request for search-based recommendations)
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    try:
        load_dataset()

        if data is None:
            abort(500, description="Dataset is not loaded")

        if request.method == 'GET':
            # Handle GET requests for keyword-based recommendations
            keywords = request.args.get('keywords', '').strip()

            if not keywords:
                return jsonify({'error': 'No search keywords provided'}), 400

            recommendations = recommender.recommend_products(data, keywords=keywords)

        elif request.method == 'POST':
            # Handle POST requests with JSON input
            request_data = request.get_json()

            if not request_data:
                return jsonify({'error': 'Invalid or missing JSON input'}), 400

            try:
                validated_data = RecommendationRequest(**request_data)
            except ValueError:
                return jsonify({'error': 'Invalid input data'}), 400

            # Infer user cluster if interaction data is provided
            if validated_data.user_interaction_data and validated_data.user_interaction_data.prices:
                user_data = pd.DataFrame({"Price": validated_data.user_interaction_data.prices})
                user_cluster = recommender.infer_user_cluster(user_data)
            else:
                user_cluster = None

            # Extract keywords and get recommendations
            keywords = recommender.extract_keywords(validated_data.keywords or "")
            recommendations = recommender.recommend_products(data, user_cluster=user_cluster, keywords=keywords)

        else:
            return jsonify({'error': 'Invalid request method'}), 405

        if recommendations.empty:
            return jsonify({'error': 'No recommendations found'}), 404

        # Convert recommendations to JSON
        recommendations_list = recommendations.to_dict(orient='records')
        return jsonify({"recommendations": recommendations_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
#python -m uvicorn ec:app --reload
#python ec.py
