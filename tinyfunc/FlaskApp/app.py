from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return "Hello from Flask on Azure Functions!"

@app.get("/hello/<name>")
def hello(name):
    return jsonify(msg=f"Hi {name}! 👋")
