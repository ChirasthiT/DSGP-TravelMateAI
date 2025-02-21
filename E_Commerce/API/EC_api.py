from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
from urllib.parse import quote
import os
from flask_pymongo import PyMongo
from pydantic import BaseModel
import pandas as pd
from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from gridfs import GridFS
import base64
import os

from E_Commerce.API.Recommender import Recommender

EC_blueprint = Blueprint('EC', __name__, template_folder='templates', static_folder='static')
client = MongoClient('mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/')
db = client['travelmateai']


@EC_blueprint.route('/EC.home')
def home():
    return render_template('EC.html')

@EC_blueprint.route('/recommend', methods=['GET'])
def recommend():
    user_budget = request.args.get('budget', '').strip().lower()
    user_district = request.args.get('district', '').strip().lower()
    user_category = request.args.get('category', '').strip().lower()

    # Fetch and preprocess data
    recommender = Recommender()
    collection = db['EC_Data']
    documents = list(collection.find())
    if not documents:
        return jsonify({"error": "No data found in the database"}), 404
    data = recommender.load_data(collection)
    data, feature_matrix = recommender.preprocess_data(data)
    try:
        recommendations = recommender.recommend(user_budget, user_district, user_category, data, feature_matrix)
    except ValueError as e:
        return jsonify({"error": f"ValueError: {str(e)}"}), 400

    # Add image data to recommendations
    recommendations_with_images = []
    for i, row in recommendations.iterrows():
        image_name = row.get("Image")
        image_name = os.path.basename(image_name)
        image_base64 = get_image_base64(image_name) if image_name else None
        recommendations_with_images.append({
            "Category": row["Category"],
            "Name": row["Name"],
            "Address": row["Address"],
            "District": row["District"],
            "Budget Level": row["Budget Level"],
            "Rating": row["Rating"],
            "Similarity": row["Similarity"],
            "Image": image_base64  # Base64-encoded image
        })

    return jsonify({"recommendations": recommendations_with_images})



@EC_blueprint.route('/back', methods=['GET'])
def go_back():
    return render_template('EC.html')


def get_image_base64(image_name):
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