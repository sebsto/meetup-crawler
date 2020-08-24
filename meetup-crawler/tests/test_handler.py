import json
import pytest
import logging

from src.meetupcrawler import app

@pytest.fixture()
def sqs_event():
    """ Generates SQS Event"""

    return {
        "Records": [
            {
            "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
            "receiptHandle": "MessageReceiptHandle",
            "body": "{ \"group\" : \"French-AWS-UG\", \"start\" : 1, \"end\" : 2 }",
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1523232000000",
                "SenderId": "123456789012",
                "ApproximateFirstReceiveTimestamp": "1523232000001"
            },
            "messageAttributes": {},
            "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
            "awsRegion": "us-east-1"
            }
        ]
    }


def test_lambda_handler(sqs_event, mocker):

    ret = app.lambda_handler(sqs_event, "")
    assert(True)
    