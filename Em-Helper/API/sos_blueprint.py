from flask import Blueprint, request, jsonify
from database import save_sos_alert

sos_blueprint = Blueprint('sos_blueprint', __name__)

@sos_blueprint.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400

    save_sos_alert(data)

    return jsonify({"status": "SOS Sent!", "data": data}), 200
