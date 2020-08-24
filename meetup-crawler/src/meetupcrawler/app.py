import os
import json
import logging

from meetupcrawler.meetupclient import MeetupClient
from meetupcrawler.db_connection import get_secret

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

    db_config = get_secret(
        region_name=os.environ['AWS_REGION'],
        secret_name=os.environ['DB_SECRET_NAME']
    )

    logger.debug(db_config)

    meetup_client = MeetupClient()

    group_infos = []
    for record in event['Records']:
        body = json.loads(record['body'])
        group_infos.append(meetup_client.members(body['group']).initial_data)

    return group_infos

if __name__ == "__main__":
    logger.info("main")
    with open('./events/event.json') as json_file:
        payload = json.load(json_file)
        ret = lambda_handler(payload, {})
        logger.debug(ret)
