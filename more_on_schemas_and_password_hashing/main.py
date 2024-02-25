from flask import Flask, jsonify, request, make_response
import psycopg
from psycopg.rows import dict_row
from time import sleep
from app import models, utils
from app.database import engine, get_db
from app.schemas import Post, PostCreate, PostBase, Usercreate, UserOut


models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)


while True:
    try:
        conn = psycopg.connect(host='localhost', dbname='APi_DEV', user='postgres', password='Dickfish1.',
                               row_factory=dict_row)
        cursor = conn.cursor()
        print("database connection successful")
        break

    except Exception as error:
        print(f"error occured as a result of {error}")
        sleep(2)


@app.route("/")
def greet():
    return {"message": "hello world!"}


@app.route("/posts", methods=["GET"])
def get_posts():
    db = next(get_db())
    posts = db.query(models.Post).all()
    return jsonify([PostBase.model_validate(post).model_dump() for post in posts])


@app.route("/posts", methods=['POST'])
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


@app.route("/posts/<int:id>", methods=["GET"])
def get_post(id):
    db = next(get_db())
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        return jsonify({"message": f"Post with id: {id} not found"}), 404
    response = PostBase.model_validate(post).model_dump()
    return jsonify(response)


@app.route("/posts/<int:id>", methods=['DELETE'])
def del_post(id):
    db = next(get_db())
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        return jsonify({"message": f"post not found with id: {id}"}), 404
    post.delete()
    db.commit()
    return jsonify({"message": "action successful"}), 204


@app.route("/update/<int:id>", methods=["PUT"])
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


@app.route("/users", methods=['POST'])
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


@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    db = next(get_db())
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        return jsonify({"message": f"User with id: {id} not found"}), 404
    response = UserOut.model_validate(user).model_dump()
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)


