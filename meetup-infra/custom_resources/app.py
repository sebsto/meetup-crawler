
import os
import json 
import uuid 
import base64 
import logging 

import boto3
from botocore.exceptions import ClientError

import psycopg2

create_meetup_group_sql = "CREATE TABLE IF NOT EXISTS meetup_group (id BIGINT, name VARCHAR, status VARCHAR, link VARCHAR, urlname VARCHAR, description VARCHAR, created BIGINT, city VARCHAR, untranslated_city VARCHAR, country VARCHAR, localized_country_name VARCHAR, localized_location VARCHAR, region2 VARCHAR, state VARCHAR, join_mode VARCHAR, visibility VARCHAR, lat NUMERIC, lon NUMERIC, members BIGINT, member_pay_fee BOOLEAN, timezone VARCHAR, last_updated_at BIGINT, raw_json JSON NOT NULL);"

create_meetup_event_sql = "CREATE TABLE IF NOT EXISTS meetup_event ( \
    id VARCHAR PRIMARY KEY, \
    utc_offset BIGINT, rsvp_limit BIGINT, headcount BIGINT, visibility VARCHAR, \
    waitlist_count BIGINT, created BIGINT, maybe_rsvp_count BIGINT, description VARCHAR, why VARCHAR, \
    how_to_find_us VARCHAR, event_url VARCHAR, yes_rsvp_count BIGINT, name VARCHAR, \
    time BIGINT, duration BIGINT, updated BIGINT, photo_url VARCHAR, \
    \
    fee_amount BIGINT, fee_accepts VARCHAR, fee_description VARCHAR, fee_currency VARCHAR, fee_label VARCHAR, fee_required VARCHAR, \
    \
    venue_country VARCHAR, venue_localized_country_name VARCHAR, venue_city VARCHAR, venue_state VARCHAR, venue_address_1 VARCHAR, \
    venue_address_2 VARCHAR, venue_name VARCHAR, venue_lon NUMERIC, venue_id BIGINT, venue_lat NUMERIC, venue_repinned BOOLEAN, \
    venue_phone VARCHAR, venue_zip VARCHAR, \
    \
    rating_count BIGINT, rating_average BIGINT, \
    \
    group_join_mode VARCHAR, group_created BIGINT, group_name VARCHAR, group_group_lon NUMERIC, group_id BIGINT, \
    group_urlname VARCHAR, group_group_lat NUMERIC, group_who VARCHAR, \
    \
    last_updated_at BIGINT, raw_json JSON NOT NULL);"

create_meetup_group_view_sql = "CREATE OR REPLACE VIEW meetup_group_latest AS \
    SELECT *  \
    FROM meetup_group AS MG \
    WHERE last_updated_at = (SELECT max(last_updated_at) FROM meetup_group WHERE MG.id = id);"

# Initialize logging with level provided as environment variable
LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'WARNING').upper()
NUMERIC_LOGLEVEL = getattr(logging, LOGLEVEL, None)
if not isinstance(NUMERIC_LOGLEVEL, int):
    raise Exception(f'Invalid log level: {NUMERIC_LOGLEVEL}')

logging.basicConfig()
logger = logging.getLogger(name="DBInitialiser")
logger.setLevel(NUMERIC_LOGLEVEL)

# verify pre-reqs env variables
if 'AWS_REGION' not in os.environ:
    raise Exception("AWS_REGION env variable is missing")

if 'DB_SECRET_ARN' not in os.environ:
    raise Exception("DB_SECRET_ARN env variable is missing")

AWS_REGION=os.environ['AWS_REGION']
DB_SECRET_ARN=os.environ['DB_SECRET_ARN']

def __executeStatement(secret, sql):
    con = None 
    
    try:
        logger.debug(f"Connecting to DB {secret['dbname']}")
        con = psycopg2.connect(**secret)
        cur = con.cursor()

        cur.execute(sql)
        
        cur.close()
        con.commit()
        logger.debug(f"commit")

    except psycopg2.DatabaseError as e:
        logger.exception(f"Can not execute { sql } statement")
        raise e
    finally:
        if con is not None:
            con.close() 

def __get_secret():

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=AWS_REGION
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        logger.debug(f"Going to retrieve secret { DB_SECRET_ARN } in region { AWS_REGION }")
        get_secret_value_response = client.get_secret_value(
            SecretId=DB_SECRET_ARN
        )

    except ClientError as e:
      logger.exception("Can not get secret")
      raise e

    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return secret
                
def __pgDSN():
    try:
        secret = __get_secret()
        secret['user'] = secret['username']
        del secret['username']
        del secret['engine']
        logger.debug(f"Got connection details for { secret['dbname'] } and user { secret['user'] }")
    except (ClientError, Exception) as e:
        logger.exception(f"Can not retrieve secret : { DB_SECRET_ARN }")
        raise e
    return secret 

def on_event(event, context):
  print(event)
  request_type = event['RequestType']
  if request_type == 'Create': return on_create(event)
  if request_type == 'Update': return on_update(event)
  if request_type == 'Delete': return on_delete(event)
  raise Exception("Invalid request type: %s" % request_type)

def on_create(event):
  props = event["ResourceProperties"]
  logger.info("create new resource with props %s" % props)

  # create data model in the database

  # 1. get the connection details  
  logger.debug("Getting connection details")
  connection_info = __pgDSN()

  # 2. execute the SQL statements
  logger.debug("Creating Meetup Group table")
  __executeStatement(connection_info, create_meetup_group_sql)
  logger.debug("Creating Meetup Event table")
  __executeStatement(connection_info, create_meetup_event_sql)
  logger.debug("Creating Meetup Group view")
  __executeStatement(connection_info, create_meetup_group_view_sql)

  physical_id = str(uuid.uuid4())
  logger.info(f"Done, returning Physical resource ID { physical_id }")
  return { 'PhysicalResourceId': physical_id }

def on_update(event):
  physical_id = event["PhysicalResourceId"]
  props = event["ResourceProperties"]
  logger.info("update resource %s with props %s" % (physical_id, props))
  # ...

def on_delete(event):
  physical_id = event["PhysicalResourceId"]
  logger.info("delete resource %s" % physical_id)
  # ...