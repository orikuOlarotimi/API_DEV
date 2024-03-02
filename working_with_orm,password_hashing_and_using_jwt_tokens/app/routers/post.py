from flask import Flask, jsonify, request, Blueprint
from app import models
from app.database import get_db
from app.schemas import PostCreate, PostBase

post_bp = Blueprint('post', __name__, url_prefix='/posts')


@post_bp.route("/", methods=["GET"])
def get_posts():
    db = next(get_db())
    posts = db.query(models.Post).all()
    return jsonify([PostBase.model_validate(post).model_dump() for post in posts])


@post_bp.route("/", methods=['POST'])
def create_post():
    db = next(get_db())
    data = request.get_json()
    user_data = PostCreate(**data)
    new_post = models.Post(**user_data.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    response_data = PostBase.model_validate(new_post)  # Convert SQLAlchemy model to Pydantic model
    return jsonify(response_data.model_dump()), 201


@post_bp.route("/<int:id>", methods=["GET"])
def get_post(id):
    db = next(get_db())
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        return jsonify({"message": f"Post with id: {id} not found"}), 404
    response = PostBase.model_validate(post).model_dump()
    return jsonify(response)


@post_bp.route("/<int:id>", methods=['DELETE'])
def del_post(id):
    db = next(get_db())
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        return jsonify({"message": f"post not found with id: {id}"}), 404
    post.delete()
    db.commit()
    return jsonify({"message": "action successful"}), 204


@post_bp.route("/<int:id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    scheme = PostCreate(**data)
    db = next(get_db())
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        return jsonify({"message": f"post not found with id: {id}"}), 404
    post_query.update(scheme.model_dump())
    db.commit()
    response = PostBase.model_validate(post).model_dump()
    return jsonify(response)