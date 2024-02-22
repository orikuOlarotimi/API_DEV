from flask import Flask, jsonify, request, make_response
import requests
import json
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
from time import sleep
from sqlalchemy.orm import Session
from app import models
from app.database import engine, SessionLocal, get_db


models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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


@app.route("/sqlalchemy", methods=["GET"])
def testing():
    db = next(get_db())
    posts = db.query(models.Post).all()
    return jsonify([post.to_dict() for post in posts])


@app.route("/posts", methods=["GET"])
def get_posts():
    # cursor.execute(""" SELECT * FROM post""")
    # posts = cursor.fetchall()
    # return jsonify({"Data": posts})
    db = next(get_db())
    posts = db.query(models.Post).all()
    return jsonify([post.to_dict() for post in posts])


@app.route("/posts", methods=['POST'])
def create_post():
    db = next(get_db())
    data = request.get_json()
    user_data = Post(**data)
    # cursor.execute(""" INSERT INTO post (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (user_data.title, user_data.content, user_data.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**user_data.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    new_post = new_post.to_dict()
    return jsonify({"data": new_post}), 201


@app.route("/posts/<int:id>", methods=["GET"])
def get_post(id):
    # cursor.execute("""SELECT * FROM post WHERE id = %s""", (id,))
    # post = cursor.fetchone()
    db = next(get_db())
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        response_body = {'message': f'post with id: {id} not found'}
        response = make_response(response_body, 404)
        return response
    post = post.to_dict()
    return jsonify({"message": post})


@app.route("/posts/<int:id>", methods=['DELETE'])
def del_post(id):
    # cursor.execute(""" DELETE FROM post WHERE id = %s RETURNING *""", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
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
    scheme = Post(**data)
    # cursor.execute(""" UPDATE post SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (scheme.title, scheme.content, scheme.published, id,))
    # updated_post = cursor.fetchone()
    # conn.commit()
    db = next(get_db())
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        return jsonify({"message": f"post not found with id: {id}"}), 404
    post_query.update(scheme.dict())
    db.commit()
    return jsonify({"message": post_query.first().to_dict()})


if __name__ == '__main__':
    app.run(debug=True)
