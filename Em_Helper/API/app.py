# from risk_model import evaluate_risk
from location import get_current_location
from emergency_action import determine_action
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


@sos_blueprint.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400

    save_sos_alert(data)

    return jsonify({"status": "SOS Sent!", "data": data}), 200


@sos_blueprint.app.route('/sos', methods=['POST'])
def handle_sos():
    data = request.json
    user_id = data.get('user_id')
    input_type = data.get('input_type')  # "call", "text", "audio"
    content = data.get('content')

    location = get_current_location(user_id)
    risk_score, risk_level = evaluate_risk(content)  # NLP model

    response = {
        "location": location,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommended_action": determine_action(risk_level)
    }

    return jsonify(response)
