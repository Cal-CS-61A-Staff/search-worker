import functools
import os

import requests
from flask import Flask, jsonify, request, redirect, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ELASTIC_SEARCH = "http://localhost:9200"
PIAZZA_INDEX = "piazza"
RESOURCE_INDEX = "resources"


@app.route("/")
def index():
    return redirect("https://cs61a.org")


def secure(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        secret = request.json["secret"]
        if secret != os.environ["SECRET"]:
            abort(401)
        return f(*args, **kwargs)
    return wrapped


@app.route("/insert/piazza", methods=["POST"])
@secure
def insert_piazza():
    post = request.json["data"]
    id = post["id"]
    resp = requests.post(f"{ELASTIC_SEARCH}/{PIAZZA_INDEX}/_doc/{id}", json=post)
    return jsonify(resp.json())


@app.route("/insert/resources", methods=["POST"])
@secure
def insert_resources():
    resources = request.json["resources"]
    requests.delete(f"{ELASTIC_SEARCH}/{RESOURCE_INDEX}")
    for resource in resources:
        print(resource)
        requests.post(f"{ELASTIC_SEARCH}/{RESOURCE_INDEX}/_doc", json=resource)
    return jsonify({"success": True})


@app.route("/query", methods=["POST"])
def query():
    piazza_params = request.json["piazza_params"]
    resource_params = request.json["resource_params"]
    piazza = requests.get(
        f"{ELASTIC_SEARCH}/{PIAZZA_INDEX}/_search", json=piazza_params
    ).json()
    resources = requests.get(
        f"{ELASTIC_SEARCH}/{RESOURCE_INDEX}/_search", json=resource_params
    ).json()
    return jsonify({"piazza": piazza, "resources": resources})


if __name__ == "__main__":
    os.environ["SECRET"] = "development"
    app.run()
