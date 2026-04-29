import json
import base64
import hashlib
from datetime import datetime

def lambda_handler(event, context):
    http_method = event.get("httpMethod", "POST")
    body = json.loads(event.get("body") or "{}")

    if http_method == "POST":
        action     = body.get("action", "analyze")
        image_data = body.get("image_base64", "")

        if not image_data:
            return _response(400, {"error": "image_base64 is required"})

        img_hash = hashlib.md5(image_data.encode()).hexdigest()
        size_kb  = round(len(image_data) * 3 / 4 / 1024, 2)

        if action == "analyze":
            result = {
                "action":     "analyze",
                "image_hash": img_hash,
                "size_kb":    size_kb,
                "format":     "JPEG",
                "width":      800,
                "height":     600,
                "processed_at": datetime.utcnow().isoformat(),
            }
        elif action == "resize":
            width  = body.get("width", 300)
            height = body.get("height", 200)
            result = {
                "action":      "resize",
                "image_hash":  img_hash,
                "new_width":   width,
                "new_height":  height,
                "processed_at": datetime.utcnow().isoformat(),
            }
        elif action == "thumbnail":
            result = {
                "action":      "thumbnail",
                "image_hash":  img_hash,
                "thumb_size":  "150x150",
                "processed_at": datetime.utcnow().isoformat(),
            }
        else:
            return _response(400, {"error": f"Unknown action: {action}"})

        return _response(200, {"status": "success", "result": result})

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
