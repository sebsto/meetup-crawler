import os
import sys
import json
import time
import logging

import boto3

from meetupcrawler.dbclient import DatabaseClient
from meetupcrawler.meetupclient import MeetupClient

# verify pre-reqs env variables
if 'AWS_REGION' not in os.environ:
    raise Exception("AWS_REGION env variable is missing")

if 'DB_SECRET_NAME' not in os.environ:
    raise Exception("DB_SECRET_NAME env variable is missing")

# Initialize logging with level provided as environment variable
LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'WARNING').upper()
NUMERIC_LOGLEVEL = getattr(logging, LOGLEVEL, None)
if not isinstance(NUMERIC_LOGLEVEL, int):
    raise Exception(f'Invalid log level: {NUMERIC_LOGLEVEL}')

logging.basicConfig()
logger = logging.getLogger(name="MeetupCrawlerLambda")
logger.setLevel(NUMERIC_LOGLEVEL)

def get_item(table, group_name):
    item_result = table.get_item(
        Key= {
            'pk' : group_name,
            'sk' : 'NOT_USED'
        }
    )
    if item_result['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(f"Can not find group: { group_name } in control database.\n{ item_result }")
    
    item = item_result['Item']    
    
    return item

def update_item(table, item):
    item['last_updated_at'] = int(time.time())
    item = table.put_item(
        Item=item
    )     
    
# I decided to let all exceptions go through to let the AWS Lambda service know about errors

def lambda_handler(event, context):
    logger.info("Meetup Crawler Lambda Handler")
    logger.debug(event)
    status = 'FAILED'

    # prepare the dynamodb connexion
    session  = boto3.session.Session()
    dynamodb = session.resource('dynamodb', region_name=os.environ['AWS_REGION'])
    table    = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

    # prepare the postgres connection
    db = DatabaseClient(
        region_name=os.environ['AWS_REGION'],
        secret_name=os.environ['DB_SECRET_NAME']
    )

    meetup = MeetupClient()

    # one SQS delivery might contains several SQS messages
    for record in event['Records']:
            
            # load the body part of the message 
            body = json.loads(record['body'])
            
            # for each meetup group in the message 
            for g in body:
                
                # get the group from control table                
                item = get_item(table, g['group'])
                
                try:
                    
                    # First, get details about the group
                    group_info = meetup.group(g['group'])
                    logger.info(f'Handling group: { group_info["name"] } ({ group_info["urlname"] })')
                    #logger.debug(group_info)
        
                    sql = db.insertGroupStmt(group_info)
                    #logger.debug(sql)
                    
                    db.executeStatement(sql)
                    logger.debug('Group data updated')
                    
                    # Second get details about their events
                    events = meetup.events(group_info, g['start'])
                    #logger.debug(events)
                    
                    for e in events:
                        logger.info(f"Handling event: { e['name'] }")
                        sql = db.insertEventsStmt(e)
                        #logger.debug(sql)
                        db.executeStatement(sql)
                        logger.debug('Event data updated')
        
                    status = "SUCCEED"
                    item['status'] = status 
                    update_item(table, item)

    
                except:
                        
                    item['status'] = status 
                    update_item(table, item)
                    
                    e = sys.exc_info()[0]
                    logger.error(f"Can not process message : { event }")
                    logger.error(e)
                    raise e   
    
        
    # failed status are not reported, because of raise e above
    return status
            

if __name__ == "__main__":
    logger.info("main")
    with open('./events/event.json') as json_file:
        payload = json.load(json_file)
        lambda_handler(payload, {})
