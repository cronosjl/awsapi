import json
import hashlib
from datetime import datetime

USERS_DB = {
    "1": {"id": "1", "username": "alice",   "email": "alice@example.com",   "role": "admin"},
    "2": {"id": "2", "username": "bob",     "email": "bob@example.com",     "role": "user"},
    "3": {"id": "3", "username": "charlie", "email": "charlie@example.com", "role": "user"},
}

def lambda_handler(event, context):
    http_method  = event.get("httpMethod", "GET")
    path_params  = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}
    body         = json.loads(event.get("body") or "{}")
    user_id      = path_params.get("id") or query_params.get("id")

    if http_method == "GET":
        if user_id:
            user = USERS_DB.get(user_id)
            if not user:
                return _response(404, {"error": f"User {user_id} not found"})
            return _response(200, {"status": "success", "user": user})
        return _response(200, {"status": "success", "users": list(USERS_DB.values()), "count": len(USERS_DB)})

    elif http_method == "POST":
        username = body.get("username")
        email    = body.get("email")
        if not username or not email:
            return _response(400, {"error": "username and email are required"})
        new_id   = str(len(USERS_DB) + 1)
        new_user = {
            "id":         new_id,
            "username":   username,
            "email":      email,
            "role":       body.get("role", "user"),
            "created_at": datetime.utcnow().isoformat(),
        }
        return _response(201, {"status": "created", "user": new_user})

    elif http_method == "PUT":
        if not user_id:
            return _response(400, {"error": "User ID is required"})
        user = USERS_DB.get(user_id)
        if not user:
            return _response(404, {"error": f"User {user_id} not found"})
        updated = {**user, **{k: v for k, v in body.items() if k != "id"}, "updated_at": datetime.utcnow().isoformat()}
        return _response(200, {"status": "updated", "user": updated})

    elif http_method == "DELETE":
        if not user_id:
            return _response(400, {"error": "User ID is required"})
        if user_id not in USERS_DB:
            return _response(404, {"error": f"User {user_id} not found"})
        return _response(200, {"status": "deleted", "user_id": user_id})

    return _response(405, {"error": "Method not allowed"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
