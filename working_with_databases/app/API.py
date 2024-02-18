from flask import Flask, jsonify, request, make_response
import requests
import json
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
from psycopg.rows import dict_row
from time import sleep

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


@app.route("/posts", methods=["GET"])
def get_posts():
    cursor.execute(""" SELECT * FROM post""")
    posts = cursor.fetchall()
    return jsonify({"Data": posts})


@app.route("/posts", methods=['POST'])
def create_post():
    data = request.get_json()
    user_data = Post(**data)
    cursor.execute(""" INSERT INTO post (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (user_data.title, user_data.content, user_data.published))
    new_post = cursor.fetchone()
    conn.commit()
    return jsonify({"data": new_post}), 201


@app.route("/posts/<int:id>", methods=["GET"])
def get_post(id):
    cursor.execute("""SELECT * FROM post WHERE id = %s""", (id,))
    post = cursor.fetchone()
    if not post:
        response_body = {'message': f'post with id: {id} not found'}
        response = make_response(response_body, 404)
        return response
    return jsonify({"message": post})


@app.route("/posts/<int:id>", methods=['DELETE'])
def del_post(id):
    cursor.execute(""" DELETE FROM post WHERE id = %s RETURNING *""", (id,))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        return jsonify({"message": f"post not found with id: {id}"}), 404
    return jsonify({"message": f"{deleted_post}, post deleted sucessfully"}), 204


@app.route("/update/<int:id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    scheme = Post(**data)
    cursor.execute(""" UPDATE post SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (scheme.title, scheme.content, scheme.published, id,))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        return jsonify({"message": f"post not found with id: {id}"}), 404
    return jsonify({"message": updated_post})


if __name__ == '__main__':
    app.run(debug=True)
