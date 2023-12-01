import json
import boto3

s3 = boto3.client("s3")
rekognition = boto3.client('rekognition', region_name="us-east-1")
tableName = "rekognition-db"
dynamodb= boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(tableName)

def lambda_handler(event, context):
    print(event)
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    
    try:
        # analyze the image
        response = index_image(bucket, key)
        print("Api Response: ", response)
        
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            faceId = response["FaceRecords"][0]["Face"]["FaceId"]
            name  = key.split(".")[0]
            store_user(faceId, name)

            return {
                'statusCode': 200,
                'body': json.dumps('Success')
            }

    except Exception as e:
        print(e)
        raise e
        


def index_image(bucket, key):
    """
    Analyze the image using Amazon Rekognition
    """
    response  = rekognition.index_faces(
        Image= {
            "S3Object":{
                "Bucket": bucket,
                "Name": key
            }
        },
        CollectionId = "trusted-individuals"
    )
    return response
    
def store_user(faceId, name):
    """
    Store the name and faceId of authorized individuals in DynamoDB
    """
    table.put_item(
        Item={
            "rekognition_id": faceId,
            "name": name
        }
    )  
        
    
