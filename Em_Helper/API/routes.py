from flask import Flask, send_from_directory, render_template
from app import sos_blueprint
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('templates', 'sos.html')

@app.route('/sos')
def sos_page():
    return send_from_directory('templates', 'sos.html')

os.makedirs('templates', exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)