from flask import jsonify, request, Blueprint
from app import models, utils
from app.database import get_db
from app.schemas import Usercreate, UserOut

user_bp = Blueprint('user', __name__, url_prefix='/users')


@user_bp.route("/", methods=['POST'])
def create_user():
    db = next(get_db())
    data = request.get_json()
    user_data = Usercreate(**data)
    hashed_password = utils.hash(user_data.password)
    user_data.password = hashed_password
    new_user = models.User(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    response_data = UserOut.model_validate(new_user)
    return jsonify(response_data.model_dump()), 201


@user_bp.route("/<int:id>", methods=["GET"])
def get_user(id):
    db = next(get_db())
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        return jsonify({"message": f"User with id: {id} not found"}), 404
    response = UserOut.model_validate(user).model_dump()
    return jsonify(response)
