from django.conf import settings
import boto3
import json


class AmazonLambdaService:
    AWS_LAMBDA_REGION_NAME = settings.AWS_LAMBDA_REGION_NAME
    AWS_LAMBDA_FUNCTION_NAME = settings.AWS_LAMBDA_FUNCTION_NAME

    def __init__(self):
        self.client = boto3.client("lambda", region_name=self.AWS_LAMBDA_REGION_NAME)

    def start(self, data):
        self.client.invoke(
            FunctionName=self.AWS_LAMBDA_FUNCTION_NAME,
            InvocationType="Event",
            Payload=json.dumps(data),
        )
