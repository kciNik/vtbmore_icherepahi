#  == routes.py
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user
from app.api import bp
from app.models import User
from app import db
from app.api.errors import bad_request

#  http POST http://localhost:5000/api/authorization name=ilya password=dog


@bp.route('/authorization', methods=['POST'])
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
    response.headers['Location'] = url_for('api.authorization', id=user.id)
    return response


@bp.route('/registration', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'name' not in data or 'email' not in data or 'login' not in data or 'password' not in data:
        return bad_request('must include name, email, login and password fields')
    if User.query.filter_by(login=data['login']).first():
        return bad_request('please use a different login')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/logout', methods=['GET', 'POST'])
def get_user(id):
    pass