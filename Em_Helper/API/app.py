from flask import Blueprint, request, jsonify
from Em_Helper.API.database import save_sos_alert
from Em_Helper.API.risk_analysis import evaluate_risk, determine_action

sos_blueprint = Blueprint('sos_blueprint', __name__)

@sos_blueprint.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400

    try:
        save_sos_alert(data, db=sos_blueprint.db)
        return jsonify({"status": "SOS Sent!", "data": data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save SOS alert: {str(e)}"}), 500


@sos_blueprint.route('/sos', methods=['POST'])
def handle_sos():
    data = request.json
    if not data or "content" not in data:
        return jsonify({"error": "Invalid request"}), 400

    user_id = data.get('user_id', 'anonymous')
    input_type = data.get('input_type', 'text')
    content = data.get('content')

    try:
        risk_score, risk_level = evaluate_risk(content)
        recommended_actions = determine_action(risk_level)

        response = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommended_action": recommended_actions
        }

        # High risk = automatically save
        if risk_level.lower() == "high":
            alert_data = {
                "user_id": user_id,
                "message": content,
                "risk_level": risk_level,
                "risk_score": risk_score,
            }
            save_sos_alert(alert_data, db=sos_blueprint.db)

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Failed to process SOS request: {str(e)}"}), 500