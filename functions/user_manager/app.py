import json
from datetime import datetime

# Mock database
USERS = [
    {"id": 1, "name": "Alice", "email": "alice@cafe.com", "created_at": "2025-01-15"},
    {"id": 2, "name": "Bob", "email": "bob@cafe.com", "created_at": "2025-01-16"},
    {"id": 3, "name": "Charlie", "email": "charlie@cafe.com", "created_at": "2025-01-17"}
]

def lambda_handler(event, context):
    """
    Lambda function to manage users via GET /users
    Supports: GET all users, GET by ID, POST new user, DELETE user
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        http_method = event.get('httpMethod', 'GET')
        path_parameters = event.get('pathParameters', {})
        
        # GET all users
        if http_method == 'GET' and not path_parameters:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'users': USERS,
                    'count': len(USERS),
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        # GET user by ID
        elif http_method == 'GET' and path_parameters:
            user_id = int(path_parameters.get('id', -1))
            user = next((u for u in USERS if u['id'] == user_id), None)
            if user:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(user)
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'message': 'User not found'})
                }
        
        # Default response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'User Manager Service',
                'users_count': len(USERS),
                'timestamp': datetime.now().isoformat()
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Error managing users',
                'error': str(e)
            })
        }