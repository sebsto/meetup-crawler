import os
import json
import logging

import meetupcrawler.db_connection as db
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


def lambda_handler(event, context):
    logger.info("Lambda Handler")
    logger.debug(event)

    # TODO this should be moved out o fthe handler to have only one DB connection per container
    db_config = db.pgDSN(
        region_name=os.environ['AWS_REGION'],
        secret_name=os.environ['DB_SECRET_NAME']
    )
    logger.debug(f"Retrieved secret for database: {db_config['dbname'] } and user { db_config['user'] }")

    meetup_client = MeetupClient()

    for record in event['Records']:
        body = json.loads(record['body'])
        for g in body:
            group_info = meetup_client.members(g['group'])
            logger.info(f'Handling Group: { group_info["name"] } ({ group_info["urlname"] })')
            logger.debug(group_info)

            sql = db.insertGroupStmt(group_info)
            logger.debug(sql)
            
            db.executeStatement(db_config, sql)
            logger.debug('Done')
            
    return

if __name__ == "__main__":
    logger.info("main")
    with open('./events/event.json') as json_file:
        payload = json.load(json_file)
        lambda_handler(payload, {})
