from users import users_service
from database import database
from main import db_path
from starlette import status
from starlette.endpoints import HTTPException
from exceptions import RegisterException, LoginException
from datetime import datetime, timedelta
import jwt


def register_command(login, password):
    if not validate(login, password):
        raise RegisterException("wrong_data")
    db = database.get_database(db_path).cursor()
    if users_service.has_user(db, login):
        raise RegisterException("existing_user")
    users_service.create_user(db, login, password)


def login_command(login, password):
    if not validate(login, password):
        raise LoginException("wrong_data")
    db = database.get_database(db_path).cursor()
    user = users_service.login(db, login, password)
    if user is None:
        raise LoginException("wrong_login")
    else:
        return user


def validate(login, password):
    if login is None or password is None:
        return False
    if not users_service.validate_login(login):
        return False
    if not users_service.validate_password(password):
        return False
    return True


jwt_secret = "dsfgsdfghiujhsfdgiuhogfsdiouhhiuosgdfigyuodfasghui0ahrg98uera"


def generate_token(login, password, user_id, exp_time=15):
    payload_data = {
        "login": login,
        "password": password,
        "exp": datetime.utcnow() + timedelta(minutes=exp_time),
        "sub": user_id
    }
    return jwt.encode(payload=payload_data, key=jwt_secret)


def decode_token(token):
    try:
        return jwt.decode(token, key=jwt_secret, algorithms=["HS256"])
    except jwt.exceptions.DecodeError:
        return False
    except jwt.exceptions.ExpiredSignatureError:
        return False
