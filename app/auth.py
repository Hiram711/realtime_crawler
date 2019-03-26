from flask_httpauth import HTTPBasicAuth
from flask import jsonify, g
from .models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_pwd(username_or_token, pwd):
    if username_or_token == '':
        return False
    if pwd == '':
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(pwd)


@auth.error_handler
def auth_error():
    response = jsonify({'error': 'Unauthorized', 'message': 'Invalid credentials'})
    response.status_code = 401
    return response
