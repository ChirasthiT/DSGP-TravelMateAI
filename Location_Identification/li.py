from flask import Blueprint, request, jsonify, render_template
# from werkzeug.utils import secure_filename
import os
from Location_Identification.API.image_indentification import Image_Identification
from flask_pymongo import PyMongo

# Blueprint Setup
li_blueprint = Blueprint('li', __name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = 'Location_Identification/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

image_identifier = Image_Identification()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@li_blueprint.route('/li.home')
def home():
    return render_template('li.html')


@li_blueprint.route('/li.identify', methods=['POST'])
def identify():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    with open(filepath, 'rb') as img_file:
        image_data = img_file.read()

    prediction = image_identifier.predict(image_data)
    mongo = li_blueprint.mongo
    location_info = mongo.db.locations.find_one({'name': prediction['prediction']})

    if location_info:
        return jsonify({
            'name': location_info['name'],
            'description': location_info['description'],
            'image_url': location_info['image_url']
        })
    return jsonify({'error': 'Location not found'}), 404


@li_blueprint.route('/li.back', methods=['GET'])
def go_back():
    return render_template('li.html')
