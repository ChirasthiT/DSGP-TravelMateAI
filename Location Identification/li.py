from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from API.image_indentification import Image_Identification
from API.loc import Location
from flask_pymongo import PyMongo

# Flask App Setup
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MONGO_URI'] = ''
app.config['MONGO_DBNAME'] = 'locationsDB'

db = PyMongo(app)

image_identifier = Image_Identification()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Routes
@app.route('/')
def home():
    return render_template('li.html')


@app.route('/identify', methods=['POST'])
def identify():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'rb') as img_file:
        image_data = img_file.read()

    prediction = image_identifier.predict(image_data)
    location_info = Location.query.filter_by(name=prediction['prediction']).first()

    if location_info:
        return jsonify({
            'name': location_info.name,
            'description': location_info.description,
            'image_url': location_info.image_url
        })
    return jsonify({'error': 'Location not found'}), 404


@app.route('/back', methods=['GET'])
def go_back():
    return render_template('li.html')


# Main Driver
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
