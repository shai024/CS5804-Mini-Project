import json
import boto3

s3 = boto3.client("s3")
rekognition = boto3.client('rekognition', region_name="us-east-1")
tableName = "rekognition-db"
dynamodb= boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(tableName)
bucket = "rekognition-needs-verification"

def lambda_handler(event, context):
    print(event)
    #key = event["queryStringParameters"]["objectKey"]
    key = event["Records"][0]["s3"]["object"]["key"]

    # change the image format to bytes
    bytes = s3.get_object(Bucket=bucket, Key=key)["Body"].read()

    # analyze the image for matches
    response = rekognition.search_faces_by_image(
        CollectionId = "trusted-individuals",
        Image={"Bytes": bytes}
    )

    # check the returned matches
    for match in response["FaceMatches"]:
        faceId = match["Face"]["FaceId"]
        confidence = match["Face"]["Confidence"]
        print("Match - Face Id:", faceId, " Confidence: ",  confidence)

        # check against the authorized individuals in dynamoDB
        ddbResponse = table.get_item(
            Key={
                "rekognition_id": faceId
            }
        )

        # The person is authorized
        if "Item" in ddbResponse:
            print("Individual is authorized", ddbResponse["Item"])
            return {
                'statusCode': 200,
                'body': json.dumps("Success! Name: {}".format(ddbResponse["Item"]["name"]))
            }
        
        # The person is NOT authorized
        else:
            print("Individual is NOT authorized")
            return {
                'statusCode': 403,
                'body': json.dumps("Individual is NOT authorized")
    }

