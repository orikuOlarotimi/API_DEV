from flask import Flask, jsonify, request, make_response
from werkzeug.exceptions import HTTPException
import requests
import json
from pprint import pprint
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = Flask(__name__)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


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
    response_data = {"message": my_post}
    return jsonify(response_data)


@app.route("/posts", methods=['POST'], )
def create_post():
    data = request.get_json()
    user_data = Post(**data)
    details = user_data.dict()
    details['id'] = randrange(0, 100000000000000000000)
    my_post.append(details)
    return {"data": details}, 201


@app.route("/posts/<int:id>", methods=["GET"])
def get_post(id):
    post = find_post(id)
    if not post:
        response_body = {'message': f'post with id: {id} not found'}
        response = make_response(response_body, 404)
        return response
    return{"message": post}


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
