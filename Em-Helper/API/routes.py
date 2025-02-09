from flask import Flask, request, jsonify
from risk_model import evaluate_risk
from location import get_current_location
from emergency_action import determine_action

app = Flask(__name__)

@app.route('/sos', methods=['POST'])
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

if __name__ == '__main__':
   app.run(debug=True)