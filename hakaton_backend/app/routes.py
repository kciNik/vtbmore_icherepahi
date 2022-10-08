from app import app
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user
from app.api import bp
from app.models import User
from app import db
from app.api.errors import bad_request
from flask_cors import cross_origin


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
    login_user(user)
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('root')
    return response
