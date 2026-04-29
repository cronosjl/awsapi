import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    method = event.get('httpMethod', 'GET')
    try:
        if method == 'GET':
            result = table.scan()
            return {'statusCode': 200, 'body': json.dumps(result.get('Items', []))}
        elif method == 'POST':
            body = json.loads(event.get('body', '{}'))
            table.put_item(Item=body)
            return {'statusCode': 201, 'body': json.dumps({'message': 'User created'})}
        return {'statusCode': 405, 'body': 'Method Not Allowed'}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
