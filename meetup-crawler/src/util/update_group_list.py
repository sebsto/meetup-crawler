import os
import time
import json
import sys
import logging
import boto3
from botocore.exceptions import ClientError

# verify pre-reqs env variables
required_env_variables = ['DYNAMODB_TABLE_NAME', 'AWS_REGION']
for e in required_env_variables:
    if e not in os.environ:
        raise Exception(f"{e} env variable is missing")

# Initialize logging with level provided as environment variable
LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'WARNING').upper()
NUMERIC_LOGLEVEL = getattr(logging, LOGLEVEL, None)
if not isinstance(NUMERIC_LOGLEVEL, int):
    raise Exception(f'Invalid log level: {NUMERIC_LOGLEVEL}')

logging.basicConfig()
logger = logging.getLogger(name="MeetupSchedulerLambda")
logger.setLevel(NUMERIC_LOGLEVEL)

# prepare the dynamodb connexion
session  = boto3.session.Session()
dynamodb = session.resource('dynamodb', region_name=os.environ['AWS_REGION'])
table    = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])  

with open("./meetup_group_list.txt") as f: 
    lines = f.readlines() 
    logger.info(f"Going to import { len(lines) } user groups")
    for line in lines: 
        now = int(time.time())
        item = dict()
        item['pk'] = line[:-1] # removing trailing \n
        item['sk'] = "GROUP"
        item['created_at'] = now
        item['last_updated_at'] = 0 
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
