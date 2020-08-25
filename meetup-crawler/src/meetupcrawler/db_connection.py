# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/

import os
import time
import json
import base64

import boto3
from botocore.exceptions import ClientError

import psycopg2

def executeStatement(secret, sql):
    con = None 
    
    try:
        con = psycopg2.connect(**secret)
        cur = con.cursor()

        cur.execute(sql)
        
        cur.close()
        con.commit()
    except psycopg2.DatabaseError as e:
        print(e)
    finally:
        if con is not None:
            con.close()  
            
def insertGroupStmt(group):
    
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
        
def get_secret(region_name: str, secret_name: str):

    # secret_name = "meetupcrawlerdatabaseSecret-pDbdefjrmmIg"
    # region_name = "eu-west-3"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
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
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret
            
def pgDSN(region_name: str, secret_name: str):
    secret = get_secret(region_name, secret_name)
    secret['user'] = secret['username']
    del secret['username']
    del secret['engine']
    return secret 
    
if __name__ == "__main__":
    secret = get_secret(region_name="eu-west-3", secret_name="meetupcrawlerdatabaseSecret-pDbdefjrmmIg")
    print(secret)
