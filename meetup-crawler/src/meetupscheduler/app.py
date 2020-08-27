import os
import time
import json
import logging

from operator import itemgetter

import boto3

# verify pre-reqs env variables
if 'AWS_REGION' not in os.environ:
    raise Exception("AWS_REGION env variable is missing")

if 'SQS_QUEUE_NAME' not in os.environ:
    raise Exception("SQS_QUEUE_NAME env variable is missing")
    
# Initialize logging with level provided as environment variable
LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'WARNING').upper()
NUMERIC_LOGLEVEL = getattr(logging, LOGLEVEL, None)
if not isinstance(NUMERIC_LOGLEVEL, int):
    raise Exception(f'Invalid log level: {NUMERIC_LOGLEVEL}')

logging.basicConfig()
logger = logging.getLogger(name="MeetupSchedulerLambda")
logger.setLevel(NUMERIC_LOGLEVEL)

def lambda_handler(event, context):
    logger.info("MeetupCrawler Scheduler Lambda Handler")
    logger.debug(event)
    
    # prepare the dynamodb connexion
    session  = boto3.session.Session()
    dynamodb = session.resource('dynamodb', region_name=os.environ['AWS_REGION'])
    table    = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
    
    # 1. full table scan to get the list of groups (not efficient but OK for a few hundreds groups)
    # TODO check FAILED status code first 
    response = table.scan()
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(f"Can not scan table : { os.environ['DYNAMODB_TABLE_NAME'] }")
    logger.info(f"Received { response['Count'] } groups")
    
    groups = response['Items']
    
    # 2. pick up the group with the smaller last update date (if multiple, pickup one randomly from the list)
    oldest_update_group = min(groups, key=itemgetter('last_updated_at')) # min returns only one item
    logger.info(f"Going to handle { oldest_update_group }")
    
    # 3. send message to crawler function (post to SQS)
    sqs      = session.resource('sqs', region_name=os.environ['AWS_REGION'])
    queue    = sqs.Queue(os.environ['SQS_QUEUE_NAME'])
    message = [{
        'group': oldest_update_group['pk'],
        'start': 0, # TODO pickup last update time here when status == success or 0 when no status exists
        'end': 0
    }]
    response = queue.send_message(
        MessageBody=json.dumps(message)
    )
    logger.debug(message)
    
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(f"Can not post message to queue : { response }")
    
    # 4. update dynamodb table with last update 
    oldest_update_group['last_updated_at'] = int(time.time())
    update = table.put_item(
        Item = oldest_update_group
    )
    logger.debug(update)
    
    logger.info("done")
    # TODO handle and report errors 
    

if __name__ == "__main__":
    logger.info("main")
    lambda_handler({}, {})

