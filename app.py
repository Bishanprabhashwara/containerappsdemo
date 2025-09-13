from flask import Flask, request, jsonify
import redis
import os

app = Flask(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

@app.route('/')
def index():
    return "Hello! Use POST /set to set a value and GET /get to retrieve it."

@app.route('/set', methods=['POST'])
def set_cache():
    # Get JSON data
    data = request.get_json()
    key = data.get("key", "mykey")        # default key = "mykey"
    value = data.get("value", "Hello from Redis!!")  # default value
    expiry = data.get("expiry", 60)       # default expiry = 60s

    r.set(key, value, ex=expiry)
    return jsonify({"message": f"Key '{key}' set with value '{value}' for {expiry} seconds"})

@app.route('/get', methods=['GET'])
def get_cache():
    key = request.args.get("key", "mykey")  # default key = "mykey"
    value = r.get(key)
    if value:
        return jsonify({"value": value})
    else:
        return jsonify({"error": "Key not found or expired"}), 404

if __name__ == "__main__":
    app.run(debug=True)
