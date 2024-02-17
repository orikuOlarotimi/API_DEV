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


my_post = [{"title": "foods", "content": "i love cooking", "id": 1, },
           {"title": "nigerian food", "content": "i love nigerian foods", "id": 2}]


def find_post(id):
    for p in my_post:
        if p['id'] == id:
            return p


def find_index(id):
    for i, p in enumerate(my_post):
        if p['id'] == id:
            return i


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
    index = find_index(id)
    if index is None:  # Check explicitly for None
        return jsonify({"message": f"post not found with id: {id}"}), 404
    my_post.pop(index)
    return jsonify({"message": "successful"}), 204


@app.route("/update/<int:id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    scheme = Post(**data)
    index = find_index(id)
    if index is None:  # Check explicitly for None
        return jsonify({"message": f"post not found with id: {id}"}), 404
    post_dict = scheme.dict()
    post_dict['id'] = id
    my_post[index] = post_dict
    return {"message": "sucessful"}


if __name__ == '__main__':
    app.run(debug=True)
