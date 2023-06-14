import os
import json


def lambda_handler(event, context):
  print(f"Getting this payload: {event}")
  print(f"This is the context: {context}")
  print(f"This is the env: {os.environ.get('trans_union_postback_url')}")

  try:
    print("returning an empty response for testing")

    return {
      'statusCode': "200",
      'body': json.dumps({
          'data': ['Hello World from TransUnion Lambda'],
          'errors': []
      }),
      'headers': {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',  
      },
      'isBase64Encoded': False  
    }
  except Exception as e:
    print(f"Internal error: {e}")
    
    return {
      'data': [],
      'errors': [{"message": f"Internal Server Error"}]
    }
