import boto3
import json
import decimal
import time 
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

session = boto3.session.Session()
dynamodb = session.resource('dynamodb', region_name='eu-west-3')
table = dynamodb.Table('meetup-crawler-dev-MeetupGroupDynamoDBTable-10NSOH0M1W28L')

with open("./scripts/meetup_group_list.txt") as f: 
    lines = f.readlines() 
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
            print("------ ERROR -----")
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise
        else:
            print(item)
