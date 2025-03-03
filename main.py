
from flask import Flask, render_template, session
from pymongo import MongoClient
from Location_Identification.li import li_blueprint
from E_Commerce.API.EC_api import EC_blueprint
from Frontend.frontend import frontend_blueprint
from Itenary.app import itinerary_blueprint

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'key'

# Register Blueprints
app.register_blueprint(li_blueprint, url_prefix='/location-identification')
app.register_blueprint(frontend_blueprint, url_prefix='/auth')
app.register_blueprint(EC_blueprint, url_prefix='/recommendation')
app.register_blueprint(itinerary_blueprint, url_prefix='/itinerary')  # Register Itinerary Blueprint

# MongoDB Connection
client = MongoClient('mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/')
db = client['travelmateai']

# Assign MongoDB to Blueprints
li_blueprint.db = db
EC_blueprint.db = db
frontend_blueprint.db = db
itinerary_blueprint.db = db  # Assign MongoDB to Itinerary Blueprint

# Routes
@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/li.home')
def feature1():
    return render_template('li.html')

@app.route('/EC.home')
def feature2():
    return render_template('EC.html')

@app.route('/itinerary.home')
def feature3():
    return render_template('itinerary.html')

# @app.route('/feature4')
# def feature4():
#     return "Feature 4 Page"

if __name__ == '__main__':
    app.run(debug=True)