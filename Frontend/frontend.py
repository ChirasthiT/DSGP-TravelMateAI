from flask import Blueprint, request, redirect, url_for, flash, render_template, jsonify, session

frontend_blueprint = Blueprint('frontend', __name__)


@frontend_blueprint.route('/main')
def main():
    return render_template('Main.html')


@frontend_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
    user = frontend_blueprint.db['user'].find_one({'username': username, 'password': password})
    if user:
        session['user_email'] = user['email']
        return jsonify({'success': True, 'redirect': url_for('frontend.main')})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@frontend_blueprint.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('newUsername', '').strip()
    email = data.get('email', '').strip()
    password = data.get('newPassword', '').strip()
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    existing_user = frontend_blueprint.db['user'].find_one({'username': username})
    if existing_user:
        return jsonify({'success': False, 'message': 'Username already exists'}), 409
    frontend_blueprint.db['user'].insert_one({'username': username, 'email': email, 'password': password})
    session['user_email'] = email
    return jsonify({'success': True, 'redirect': url_for('frontend.main')})
