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


config = {
    "settings": {
        "analysis": {
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_keywords": {"type": "keyword_marker", "keywords": ["example"]},
                "english_stemmer": {"type": "stemmer", "language": "english"},
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english",
                },
                "zero_prefix_remover": {
                    "type": "pattern_replace",
                    "pattern": r"0([0-9])+",
                    "replacement": r"$1",
                },
            },
            "analyzer": {
                "default": {
                    "tokenizer": "standard",
                    "char_filter": ["html_strip"],
                    "filter": [
                        "english_possessive_stemmer",
                        "lowercase",
                        "english_stop",
                        "english_keywords",
                        "english_stemmer",
                        "zero_prefix_remover",
                    ],
                }
            },
        }
    }
}


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


@app.route("/clear/piazza", methods=["POST"])
@secure
def clear_piazza():
    requests.delete(f"{ELASTIC_SEARCH}/{PIAZZA_INDEX}").json()
    return jsonify(
        requests.put(f"{ELASTIC_SEARCH}/{PIAZZA_INDEX}", json=config).json()
    )


@app.route("/insert/piazza", methods=["POST"])
@secure
def insert_piazza():
    posts = request.json["data"]
    for post in posts:
        id = post["id"]
        requests.post(f"{ELASTIC_SEARCH}/{PIAZZA_INDEX}/_doc/{id}", json=post)
    return jsonify({"success": True})


@app.route("/clear/resources", methods=["POST"])
@secure
def clear_resources():
    requests.delete(f"{ELASTIC_SEARCH}/{RESOURCE_INDEX}").json()
    return jsonify(
        requests.put(f"{ELASTIC_SEARCH}/{RESOURCE_INDEX}", json=config).json()
    )


@app.route("/insert/resources", methods=["POST"])
@secure
def insert_resources():
    resources = request.json["resources"]
    for resource in resources:
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
