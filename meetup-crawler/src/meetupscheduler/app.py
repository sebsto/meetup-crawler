import os
import time
import json
import logging

from operator import itemgetter

import boto3
from botocore.exceptions import ClientError

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

def initial_table_load(table):
    with open("./meetup_group_list.txt") as f: 
        lines = f.readlines() 
        logger.info(f"Going to import { len(lines) } user groups")
        for line in lines: 
            now = int(time.time())
            item = dict()
            item['pk'] = line[:-1] # removing trailing \n
            item['sk'] = "NOT_USED"
            item['created_at'] = now
            item['last_updated_at'] = now
            try:
                # Update database
                update = table.put_item(
                    Item = item
                )
            except (Exception, ClientError) as e:
                logger.exception("------ ERROR -----")
                if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                    logger.error(e.response['Error']['Message'])
                else:
                    raise e
            else:
                print(item)
        logger.info(f"Done")

def table_scan(table):
    response = table.scan()
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(f"Can not scan table : { os.environ['DYNAMODB_TABLE_NAME'] }")
    logger.info(f"Received { response['Count'] } groups")    
    return response 

def send_message(session, group, delay=0):
    sqs      = session.resource('sqs', region_name=os.environ['AWS_REGION'])
    queue    = sqs.Queue(os.environ['SQS_QUEUE_NAME'])
    message = [{
        'group': group['pk'],
        'start': 0, # TODO pickup last update time here when status == success or 0 when no status exists
        'end': 0
    }]
    response = queue.send_message(
        MessageBody=json.dumps(message),
        DelaySeconds = delay
    )
    logger.debug(message)
    
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(f"Can not post message to queue : { response }")  
    return response 

def lambda_handler(event, context):
    logger.info("MeetupCrawler Scheduler Lambda Handler")
    logger.debug(event)
    
    # prepare the dynamodb connexion
    session  = boto3.session.Session()
    dynamodb = session.resource('dynamodb', region_name=os.environ['AWS_REGION'])
    table    = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
    
    # 1. full table scan to get the list of groups (not efficient but OK for a few hundreds groups)
    # TODO check groups with FAILED status code first 
    response = table_scan(table)
    
    if response['Count'] == 0:
        # first run, let's load the table first 
        initial_table_load(table)

        # read the table again
        response = table_scan(table)

        # schedule an initial query for each group 
        logger.info("Triggering initial load")
        for i, group in enumerate(response['Items'],start = 1):
            logger.info(f"Going to handle #{i} - { group }")
            # sending message with 15 delays, up to the maximum 900 seconds
            response = send_message(session, group, (i * 15) % 900)
        
        # Machine is started, the crawler function will now handle all the messages
        return 

    groups = response['Items']
    
    # 2. pick up the group with the smaller last update date (if multiple, pickup one randomly from the list)
    oldest_update_group = min(groups, key=itemgetter('last_updated_at')) # min returns only one item
    logger.info(f"Going to handle { oldest_update_group }")
    
    # 3. send message to crawler function (post to SQS)
    send_message(session, oldest_update_group)
    
    logger.info("done")
    # TODO handle and report errors 
    

if __name__ == "__main__":
    logger.info("main")
    lambda_handler({}, {})

