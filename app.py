from flask import Flask, request, jsonify
import redis
import os

app = Flask(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redisapp")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")  # Optional; required for Azure Cache for Redis
REDIS_SSL = os.getenv("REDIS_SSL", "0").lower() in {"1", "true", "yes"}

# Connect to Redis (no immediate network call; connection happens on first command)
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    ssl=REDIS_SSL,
    decode_responses=True,
)

@app.route('/')
def index():
    return "Hello! Use POST /set to set a value and GET /get to retrieve it."

@app.route('/set', methods=['POST'])
def set_cache():
    data = request.get_json() or {}
    key = data.get("key", "mykey")
    value = data.get("value", "Hello from Redis!!")
    expiry = data.get("expiry", 60)

    try:
        r.set(key, value, ex=expiry)
        return jsonify({"message": f"Key '{key}' set with value '{value}' for {expiry} seconds"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get', methods=['GET'])
def get_cache():
    key = request.args.get("key", "mykey")
    try:
        value = r.get(key)
        if value:
            return jsonify({"value": value})
        else:
            return jsonify({"error": "Key not found or expired"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("FLASK_DEBUG", "0") == "1")
