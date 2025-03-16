from flask import Blueprint, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from Location_Identification.API.image_indentification import Image_Identification

# Blueprint Setup
li_blueprint = Blueprint('li', __name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = 'Location_Identification/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedev(UPLOAD_FOLDER)

image_identifier = Image_Identification()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@li_blueprint.route('/li.home')
def home():

    return render_template('li.html')


def add_user_history(user_email, location):
    db = li_blueprint.db
    user = db['user'].find_one({'email': user_email})
    if not user:
        return
    db['user_location_history'].insert_one({
        'user_id': user['_id'],
        'location': location,
        'timestamp': datetime.utcnow()
    })


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

    if prediction == 'Unknown':
        return jsonify({'error': 'Location not found'}), 404

    db = li_blueprint.db
    collection = db['location_info']
    location_info = collection.find_one({'name': prediction})

    if location_info:
        if 'user_email' in session:
            add_user_history(session['user_email'], prediction)
        return jsonify({
            'prediction': prediction,
            'name': location_info['name'],
            'historical_info': location_info['historical_info'],
            'fun_facts': location_info['fun_facts'],
            'image_url': location_info['image_file'],
            'nearby_locations': location_info['nearby_locations'],
            'title': location_info['title']
        })
    return jsonify({'error': 'Location not found'}), 404


@li_blueprint.route('/history', methods=['GET'])
def get_history():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify([])
    db = li_blueprint.db
    user = db['user'].find_one({'email': user_email})
    if not user:
        return jsonify([])
    history_entries = db['user_location_history'].find({'user_id': user['_id']}).sort('timestamp', -1)
    location_collection = db['location_info']
    history_list = []
    for entry in history_entries:
        location_info = location_collection.find_one({'name': entry['location']}) or {}
        history_list.append({
            'location': entry['location'],
            'timestamp': entry['timestamp'].isoformat(),
            'image_url': location_info.get('image_file', ''),
            'title': location_info.get('title', '')
        })
    return jsonify(history_list)


@li_blueprint.route('/back', methods=['GET'])
def go_back():
    return render_template('li.html')
