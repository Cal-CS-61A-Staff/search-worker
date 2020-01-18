import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/insert/piazza")
def insert():
    id =
    resp = requests.post("http://localhost:9200/piazza/_doc/{}".format(id), json={
        "name": "Bob Cat",
    })
    return jsonify(resp.json())


@app.route("/query")
def query():
    resp = requests.get("http://localhost:9200/customer/_doc/1", json={
        "name": "Bob Cat",
    })
    return jsonify(resp.json())


if __name__ == '__main__':
    app.run()
