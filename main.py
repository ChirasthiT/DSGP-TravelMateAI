from flask import Flask, render_template
from pymongo import MongoClient
from Location_Identification.li import li_blueprint
from Frontend.frontend import frontend_blueprint

app = Flask(__name__, template_folder='templates', static_folder='static')
app.register_blueprint(li_blueprint, url_prefix='/location-identification')
app.register_blueprint(frontend_blueprint, url_prefix='/auth')

client = MongoClient('mongodb+srv://admin:admindsgp66@dsgp.e5yrm.mongodb.net/')
db = client['travelmateai']

li_blueprint.db = db
frontend_blueprint.db = db

@app.route('/')
def home():
    return render_template('landing.html')


@app.route('/li.home')
def feature1():
    return render_template('li.html')


@app.route('/EC.home')
def feature2():
    return render_template('EC.html')


# @app.route('/feature3')
# def feature3():
#     return "Feature 3 Page"


# @app.route('/feature4')
# def feature4():
#     return "Feature 4 Page"


if __name__ == '__main__':
    app.run(debug=True)

