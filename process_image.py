import json
import boto3
import base64
import uuid

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        image_data = base64.b64decode(body.get('image', ''))
        key = f"images/{uuid.uuid4()}.jpg"
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image processed', 'key': key})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
