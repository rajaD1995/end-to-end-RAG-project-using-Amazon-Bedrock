import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime

def blog_generate_using_bedrock(blogtopic: str) -> str:
    """Generate a blog post using Meta Llama3 on AWS Bedrock."""
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    model_id = "meta.llama3-70b-instruct-v1:0"

    formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    Write a short, engaging blog about: {blogtopic}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
    }

    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(native_request),
            contentType="application/json",
            accept="application/json"
        )
    except ClientError as e:
        print(f"AWS error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

    model_response = json.loads(response["body"].read())
    return model_response.get("generation", "").strip()

def save_blog_to_s3(s3_key,s3_bucket,generate_blog):
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = generate_blog)
        print("Code saved to s3")

    except Exception as e:
        print("Error when saving the code to s3")



def lambda_handler(event, context):
    # TODO implement 
    event=json.loads(event['body'])
    blogtopic=event['blog_topic']
    generate_blog=blog_generate_using_bedrock(blogtopic=blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_key = f"blogs/{blogtopic.replace(' ', '_')}_{current_time}.txt"
        s3_bucket = "aws_bedrock_counsol"  # Replace with your S3 bucket name
        save_blog_to_s3(s3_key,s3_bucket,generate_blog)
    else:
        print("Blog generation failed.")

    return{
        'statusCode':200,
        'body':json.dumps('Blog Generation is completed')
    }