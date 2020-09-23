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

def table_scan(table):
    response = table.scan()
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(f"Can not scan table : { os.environ['DYNAMODB_TABLE_NAME'] }")
    logger.info(f"Received { response['Count'] } groups")    
    return response 

def update_item(table, item):
    try:
        # Update database
        update = table.put_item(
            Item = item
        )
        return update
    except (Exception, ClientError) as e:
        logger.exception("------ ERROR -----")
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.error(e.response['Error']['Message'])
        else:
            raise e
    else:
        print(item)    

def delete_item(table, item):
    try:
        # Delete item
        delete = table.delete_item(
            Key = {
                'pk': item['pk'],
                'sk': item['sk']
            }
        )
        return delete
    except (Exception, ClientError) as e:
        logger.exception("------ ERROR -----")
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.error(e.response['Error']['Message'])
        else:
            raise e
    else:
        print(item)    

response = table_scan(table)
old_group_to_delete = list(filter(lambda x: x['sk'] == 'NOT_USED', response['Items'] ))
logger.info(f"Updating { len(old_group_to_delete) } groups")    
for g in old_group_to_delete:
    
    # update new item  with old's dates 
    item = dict()
    item['pk'] = g['pk']
    item['sk'] = 'GROUP'
    item['created_at'] = g['created_at']
    item['last_updated_at'] = g['last_updated_at']
    item['status'] = g['status']
    update_item(table, item)

    #delete old 
    delete_item(table, g)
logger.info(f"Done")    
