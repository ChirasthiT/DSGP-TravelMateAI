import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from gridfs import GridFS
import base64
import os
from flask import session


from E_Commerce.API.Recommender import Recommender

EC_blueprint = Blueprint('EC', __name__, template_folder='templates', static_folder='static')

@EC_blueprint.route('/EC.home')
def home():
    return render_template('EC.html')

@EC_blueprint.route('/recommend', methods=['GET'])
def recommend():
    db = EC_blueprint.db

    if 'user_email' not in session:
        print("User not logged in")

    userEmail = session['user_email']  # Retrieve username from session
    user_budget = get_user_Budget(userEmail)
    user_district = get_user_district(userEmail)

    # Fetch and preprocess data
    recommender = Recommender(db)
    collection = db['EC_Data']
    documents = list(collection.find())
    if not documents:
        return jsonify({"error": "No data found in the database"}), 404
    data = recommender.load_data(collection)
    data, feature_matrix = recommender.preprocess_data(data)
    try:
        recommendations = recommender.recommend(user_budget, user_district, data, feature_matrix)
        ibcf_recommendations = recommender.item_based_recommend(userEmail, user_district, top_n=10)
        print(recommendations)
        print(ibcf_recommendations)
    except ValueError as e:
        return jsonify({"error": f"ValueError: {str(e)}"}), 400

    # Add image data to recommendations
    recommendations_with_images = []
    for i, row in recommendations.iterrows():
        image_name = row.get("Image")
        image_name = os.path.basename(image_name)
        image_base64 = get_image_base64(image_name) if image_name else None
        recommendations_with_images.append({
            "Source": row["Source"],
            "Name": row["Name"],
            "Address": row["Address"],
            "District": row["District"],
            "Budget Level": row["Budget Level"],
            "Rating": row["Rating"],
            "Similarity": row["Similarity"],
            "Image": image_base64  # Base64-encoded image
        })

    ibcf_recommendations_with_images = []
    for i, row in ibcf_recommendations.iterrows():
            image_name = row.get("Image")
            image_name = os.path.basename(image_name)
            image_base64 = get_image_base64(image_name) if image_name else None
            ibcf_recommendations_with_images.append({
                "Source": row["Source"],
                "Name": row["Name"],
                "Address": row["Address"],
                "District": row["District"],
                "Budget Level": row["Budget Level"],
                "Rating": row["Rating"],
                "Similarity": row["Score"],
                "Image": image_base64  # Base64-encoded image
            })

    return jsonify({
        "CBrecommendations": recommendations_with_images,
        "IBCrecommendations": ibcf_recommendations_with_images
    })


@EC_blueprint.route('/log_click', methods=['POST'])
def log_click():
    db = EC_blueprint.db  # Get the database instance
    user_clicks_collection = db["ECuser_clicks"]  # Collection to store clicks

    if 'user_email' not in session:
        return jsonify({"error": "User not logged in"}), 401  # Unauthorized

    user_email = session['user_email']
    data = request.json

    required_fields = ["name", "district"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400  # Bad request

    # Prepare click log entry
    click_entry = {
        "user_email": user_email,
        "name": data["name"],  # Recommendation name
        "district": data["district"],
        "budget": data["budget"],
        "timestamp": pd.Timestamp.utcnow()
    }

    # Insert into MongoDB
    user_clicks_collection.insert_one(click_entry)

    return jsonify({"message": "Click logged successfully"}), 200


@EC_blueprint.route('/back', methods=['GET'])
def go_back():
    return render_template('EC.html')


def get_image_base64(image_name):
    db = EC_blueprint.db
    fs = GridFS(db)
    images_metadata_collection = db['images_EC']
    metadata = images_metadata_collection.find_one({'image_name': image_name})

    if not metadata:
        return None  # Image not found

    file_id = metadata['file_id']

    try:
        image_file = fs.get(file_id)
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        return image_base64
    except Exception as e:
        print(f"Error retrieving image {image_name}: {e}")
        return None

def get_user_Budget(user_name):
    db = EC_blueprint.db
    user_db_collection = db["user"]
    user_budget = user_db_collection.find_one({"email": user_name}, {"_id": 0})
    return user_budget['budget']
def get_user_district(user_name):
    db = EC_blueprint.db
    user_db_collection = db["user"]
    user_budget = user_db_collection.find_one({"email": user_name}, {"_id": 0})
    return user_budget['district']
