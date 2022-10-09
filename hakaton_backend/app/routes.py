from app import app
from flask import url_for, request, jsonify, session
from flask_login import current_user, login_user, login_required
from app.api import bp
from app.models import User
from app import db
from app.api.errors import bad_request, error_response
from flask_cors import cross_origin
from app.auth import token_auth


@app.route('/')
@cross_origin()
def root():
    return 'Hello'

#  http POST http://localhost:5000/api/authorization login=ilya password=dog


@app.route('/api/authorization', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json() or {}
    if 'login' not in data or 'password' not in data:
        return bad_request('must include login and password fields')
    user = User.query.filter_by(login=data['login']).first()
    if user is None:
        return bad_request('please use a different login')
    if not user.check_password(data['password']):
        return bad_request('wrong password')
    login_user(user, remember=True)
    session['user_id'] = user.id
    response = jsonify(user.to_dict())
    response.status_code = 200
    response.headers['Location'] = url_for('root')
    return response


@app.route('/api/admin', methods=['GET'])
@cross_origin()
@token_auth.login_required
def get_admin():
    if token_auth.current_user().role == 'Admin':
        return jsonify(token_auth.current_user().to_dict())
    else:
        return error_response(403, 'user is not admin')


@app.route('/api/create_task', methods=['GET'])
@cross_origin()
@token_auth.login_required
def create_task():
    if current_user.role != 'Admin':
        return error_response(403, 'user is not admin')


