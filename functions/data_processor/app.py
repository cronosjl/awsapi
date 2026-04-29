import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda function to process data via POST /data
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Parse the body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Process data
        response_data = {
            'message': 'Data processed successfully',
            'timestamp': datetime.now().isoformat(),
            'received_data': body,
            'status': 'success'
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
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
                'message': 'Error processing data',
                'error': str(e)
            })
        }