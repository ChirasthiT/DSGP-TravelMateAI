from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from Location_Identification.API.image_indentification import Image_Identification
from flask_pymongo import PyMongo

# Blueprint Setup
li_blueprint = Blueprint('li', __name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = 'Location_Identification/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedev(UPLOAD_FOLDER)

image_identifier = Image_Identification()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@li_blueprint.route('/li.home')
def home():
    return render_template('li.html')


@li_blueprint.route('/identify', methods=['POST'])
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
    print(prediction)

    mongo = li_blueprint.mongo
    location_info = (mongo.travelmateai.location_info.find_one({'name': prediction['prediction']}))

    if location_info:
        return jsonify({
            'name': location_info['name'],
            'historical_info': location_info['historical_info'],
            'fun_facts': location_info['fun_facts'],
            'image_url': location_info['image_file'],
            'nearby_locations': location_info['nearby_locations'],
            'title': location_info['title']
        })
    return jsonify({'error': 'Location not found'}), 404


@li_blueprint.route('/back', methods=['GET'])
def go_back():
    return render_template('li.html')
