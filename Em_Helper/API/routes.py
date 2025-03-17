from flask import Flask, request, jsonify
from risk_model import evaluate_risk
from location import get_current_location
from emergency_action import determine_action

app = Flask(__name__)



if __name__ == '__main__':
   app.run(debug=True)