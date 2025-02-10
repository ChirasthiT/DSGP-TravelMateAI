from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
from urllib.parse import quote
import os
from Recommender import Recommender
from flask_pymongo import PyMongo
from pydantic import BaseModel
import pandas as pd
from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient

EC_blueprint = Blueprint('EC', __name__, template_folder='templates', static_folder='static')
client = MongoClient('mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/')
db = client['travelmateai']


@EC_blueprint.route('/EC.home')
def home():
    return render_template('EC.html')

@EC_blueprint.route('/Recommend', methods=['GET'])
def recommend():
    user_budget = request.args.get('budget', '').lower()
    user_district = request.args.get('district', '').lower()
    user_category = request.args.get('category', '').lower()

    recommender = Recommender()

    collection = db['EC_Data']
    data = recommender.load_data(collection)
    data, feature_matrix = recommender.preprocess_data(data)

    recommendations = recommender.recommend(user_budget, user_district, user_category, data, feature_matrix)

    return render_template('EC.html', recommendations=recommendations.to_dict(orient="records"))


@EC_blueprint.route('/back', methods=['GET'])
def go_back():
    return render_template('EC.html')
