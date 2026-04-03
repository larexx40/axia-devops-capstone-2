from flask import Flask, jsonify
from database import get_users
from utils import calculate_internal_metric
import config

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY


@app.route("/")
def home():
    return jsonify({
        "message": "Internal Utility Service Running",
        "environment": config.ENVIRONMENT
    })


@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200


@app.route("/users")
def users():
    return jsonify(get_users())


@app.route("/metric/<int:a>/<int:b>")
def metric(a, b):
    result = calculate_internal_metric(a, b)
    if result is None:
        return jsonify({"error": "Division by zero is not allowed"}), 400
    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
