from flask import request, current_app
from flask_jwt_extended import current_user, decode_token, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

from app.models.user import User


def jwt_authenticate(email, password):
    """
    helper function to authenticate user if credentials are correct
    :param email:
    :param password:
    :return:
    """
    user = User.query.filter_by(email=email.strip(), deleted_at=None).first()
    if user is None:
        return None
    auth_ok = user.facebook_login_hash == password or user.is_correct_password(password)
    if auth_ok:
        return user
    else:
        return None


def jwt_user_loader(jwt_header, jwt_data):
    return User.query.filter_by(id=int(jwt_data['sub']), deleted_at=None).first()


def _encoded_access_token():
    """Reads the encoded access token from the configured header or cookie"""
    config = current_app.config
    locations = config.get('JWT_TOKEN_LOCATION', ['headers'])
    if isinstance(locations, str):
        locations = [locations]

    if 'headers' in locations:
        header = request.headers.get(config.get('JWT_HEADER_NAME', 'Authorization'), '')
        parts = header.split()
        header_type = config.get('JWT_HEADER_TYPE', 'Bearer')
        if len(parts) == 2 and parts[0] == header_type:
            return parts[1]

    if 'cookies' in locations:
        cookie = request.cookies.get(config.get('JWT_ACCESS_COOKIE_NAME', 'access_token_cookie'))
        if cookie:
            return cookie

    return None


def get_identity():
    """
    To be used only if identity for expired tokens is required, otherwise use current_user from flask_jwt_extended
    :return:
    """
    try:
        verify_jwt_in_request()
        return current_user
    except (JWTExtendedException, PyJWTError):
        pass

    token = _encoded_access_token()
    if token:
        try:
            # Signature is still verified, only the expiry is ignored
            jwt_data = decode_token(token, allow_expired=True)
        except (JWTExtendedException, PyJWTError):
            return None
        if jwt_data.get('type') == 'access':
            return jwt_user_loader({}, jwt_data)

    return None
