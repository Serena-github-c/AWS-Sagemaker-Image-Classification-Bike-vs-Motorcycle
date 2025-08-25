# function 1 : serialize image data
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = "test/bicycle_s_000059.png"
    bucket = "sagemaker-us-east-1-423623866303"

    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket,key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data.decode('utf-8'),
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }




## function 2 : classify
import json
import boto3
import base64

# Fill this in with the name of your deployed model
ENDPOINT = "image-classifier-endpoint-23-aug-2pm"
runtime = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):
    print("recieved event:", json.dumps(event))
    
    #extract the body from the event
    if 'body' in event:
        payload = event['body']
    else:
        payload = event

    # Decode the image data
    image = base64.b64decode(payload["image_data"])

    # Call SageMaker endpoint
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType="image/png",
        Body=image
    )

    # Make a prediction
    inferences = json.loads(response["Body"].read().decode("utf-8"))
 
    # We return the data back to the Step Function    
    payload["inferences"] = inferences
    return {
        'statusCode': 200,
        'body': payload
    }
    
    
    
## function 3 : filter
import json

THRESHOLD = .93

def lambda_handler(event, context):
    # Extract the body from the event
    if 'body' in event:
        data = event['body']
    else:
        data = event

    # Grab the inferences from the event
    inferences = data["inferences"]  # convert string to float

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(float(val) >= THRESHOLD for val in inferences)

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }


