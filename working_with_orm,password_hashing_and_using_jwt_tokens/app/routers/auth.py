from flask import Flask, jsonify, request, Blueprint
from app import models, utils, oath2
from app.database import get_db
from app.schemas import UserLogin

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route("/", methods=["POST"])
def login():
    db = next(get_db())
    data = request.get_json()
    user_credentials = UserLogin(**data)
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if user and utils.verify(user_credentials.password, user.password):
        access_token = oath2.create_access_token(data={"user_id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}, 200
    else:
        return jsonify({"message": "Invalid Credentials"}), 401
