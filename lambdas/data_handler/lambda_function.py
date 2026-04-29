import json

def lambda_handler(event, context):
    http_method = event.get("httpMethod", "GET")
    body = json.loads(event.get("body") or "{}")

    if http_method == "GET":
        data = {
            "items": [
                {"id": 1, "name": "Item Alpha", "value": 100},
                {"id": 2, "name": "Item Beta",  "value": 200},
                {"id": 3, "name": "Item Gamma", "value": 300},
            ]
        }
        return _response(200, {"status": "success", "data": data})

    elif http_method == "POST":
        name  = body.get("name", "Unknown")
        value = body.get("value", 0)
        new_item = {"id": 99, "name": name, "value": value, "created": True}
        return _response(201, {"status": "created", "item": new_item})

    elif http_method == "PUT":
        item_id      = body.get("id")
        updated_name = body.get("name", "Updated")
        return _response(200, {"status": "updated", "id": item_id, "name": updated_name})

    elif http_method == "DELETE":
        item_id = body.get("id")
        return _response(200, {"status": "deleted", "id": item_id})

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
