from flask import Flask, request, jsonify
from flask_cors import CORS
from database import save_sos_alert

app = Flask(__name__)
CORS(app)

@app.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400

    save_sos_alert(data)

    return jsonify({"status": "SOS Sent!", "data": data}), 200

if __name__ == '__main__':
    app.run(debug=True)