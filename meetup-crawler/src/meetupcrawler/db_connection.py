# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/

import os
import time
import json
import base64
import logging

import boto3
from botocore.exceptions import ClientError

import psycopg2

class DatabaseClient(object):
    
    # TODO should rewrite the connection lifecycle to have only one DB connection per container
    def __init__(self, region_name: str, secret_name: str):

        # Initialize logging with level provided as environment variable
        LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'WARNING').upper()
        NUMERIC_LOGLEVEL = getattr(logging, LOGLEVEL, None)
        if not isinstance(NUMERIC_LOGLEVEL, int):
            raise Exception(f'Invalid log level: {NUMERIC_LOGLEVEL}')
        
        logging.basicConfig()
        self.logger = logging.getLogger(name="DBConnection")
        self.logger.setLevel(NUMERIC_LOGLEVEL)
        
        self.region_name = region_name 
        self.secret_name = secret_name
        self.secret = self.__pgDSN() 

    def executeStatement(self, sql):
        con = None 
        
        try:
            self.logger.debug(f"Connecting to DB {self.secret['dbname']}")
            con = psycopg2.connect(**self.secret)
            cur = con.cursor()
    
            cur.execute(sql)
            
            cur.close()
            con.commit()
            self.logger.debug(f"commit")
    
        except psycopg2.DatabaseError as e:
            self.logger.error(f"Can not execute { sql } statement")
            self.logger.error(e)
        finally:
            if con is not None:
                con.close()  
                
    def insertGroupStmt(self, group):
        
        table_name = 'meetup_group'
        fields_to_ignore=['organizer', 'who', 'group_photo', 'key_photo', 'category', 'meta_category']
        type_association={ 'str' : 'VARCHAR', 'bool' : 'BOOLEAN', 'int' : 'BIGINT', 'float' : 'NUMERIC'}
            
        all_fields = [list(group.keys())][0]
        columns = [x for x in all_fields if x not in fields_to_ignore]
        values = ''
        for c in columns:
            quote = ""
            value = group[c]
            if type(value).__name__ == 'str':
                quote = "'"
                value = group[c].replace("'", "''")
            values += f' {quote}{value}{quote}, '
    
        columns.append( 'last_updated_at , raw_json')
        json_str = json.dumps(group,ensure_ascii=False).replace("'", "''")
        values += f' { int(time.time()) }, \' { json_str } \' '
        #values = values[:-2]
        
        sql = f'INSERT INTO {table_name} ( {", ".join(columns) } ) VALUES ( { values } );'    
        return sql
            
    def __get_secret(self):
    
        # secret_name = "meetupcrawlerdatabaseSecret-pDbdefjrmmIg"
        # region_name = "eu-west-3"
    
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )
    
        # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
        # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        # We rethrow the exception by default.
    
        try:
            self.logger.debug(f"Going to retrieve secret { self.secret_name } in region { self.region_name }")
            get_secret_value_response = client.get_secret_value(
                SecretId=self.secret_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
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
                
    def __pgDSN(self):
        try:
            secret = self.__get_secret()
            secret['user'] = secret['username']
            del secret['username']
            del secret['engine']
            self.logger.debug(f"Got connection details for { secret['dbname'] } and user { secret['user'] }")
        except (ClientError, Exception) as e:
            self.logger.error(f"Can not retrieve secret : { self.secret_name }")
            self.logger.error(e)
        return secret 
    
if __name__ == "__main__":
    db_connection = DatabaseClient(region_name="eu-west-3", secret_name="meetupcrawlerdatabaseSecret-IotH2oBYYAAG")
    print(db_connection.secret)
