import json
import time

import psycopg2

# do not use, this was created early on to create the data structure and experiment the database code
# I am keeping it here for documentation purposes
raise Exception("Outdated script - do not use")

group_table_name = 'meetup_group'
group_fields_to_ignore=['organizer', 'who', 'group_photo', 'key_photo', 'category', 'meta_category']

event_table_name = 'meetup_event'
event_fields_to_ignore = [ 'group', 'venue', 'rating', 'status']
event_fields_to_flatten = [ 'venue', 'rating', 'group' ]

type_association={ 'str' : 'VARCHAR', 'bool' : 'BOOLEAN', 'int' : 'BIGINT', 'float' : 'NUMERIC'}

def createGroupTable():
    with open('./events/group-info.json') as json_file:
        payload = json.load(json_file)
        group = payload[0]
        all_fields = [list(x.keys()) for x in payload][0]
        columns = [x for x in all_fields if x not in group_fields_to_ignore]
    
        field_list = ''
        for c in columns:
            # { (" PRIMARY KEY" if c == "id" else "") } not using PK because 
            field_list += f'{c} {type_association[type(group[c]).__name__]}, '
            
        field_list += 'last_updated_at BIGINT, raw_json JSON NOT NULL'  
        #field_list = field_list[:-2]

        sql = f'CREATE TABLE IF NOT EXISTS {group_table_name} ({field_list});'
        return sql

def createEventTable():
    with open('./events/group-events.json') as json_file:
        payload = json.load(json_file)
        event = payload[1]
        all_fields = [list(event.keys())][0]
        
        if 'rsvp_limit' not in all_fields:
            raise Exception("rsvp limit field absent")
            
        columns = [x for x in all_fields if x not in event_fields_to_ignore]


        # add columns for structures to flatten, prefixed by the entry name
        for f in event_fields_to_flatten:
            additional_columns = [ f + '_' + c for c in [list(event[f].keys())][0] ]
            columns += additional_columns

        field_list = ''
        for c in columns:
            if c in event:
                # columns from the root object 
                # { (" PRIMARY KEY" if c == "id" else "") } not using PK because 
                field_list += f'{c} {type_association[type(event[c]).__name__]}, '
            else: 
                # columns from flattened objects 
                fields = c.split('_', 1)
                field_list += f'{c} {type_association[type(event[fields[0]][fields[1]]).__name__]}, '
            
        field_list += 'last_updated_at BIGINT, raw_json JSON NOT NULL'  
        #field_list = field_list[:-2]

        sql = f'CREATE TABLE IF NOT EXISTS {event_table_name} ({field_list});'
        return sql


def createGroupInsertStmt():
    with open('./events/group-info.json') as json_file:
        payload = json.load(json_file)
        group = payload[0]
        all_fields = [list(x.keys()) for x in payload][0]
        
        columns = [x for x in all_fields if x not in group_fields_to_ignore]

        values = ''
        for c in columns:
            quote = ""
            value = group[c]
            if type(value).__name__ == 'str':
                quote = "'"
                value = group[c].replace("'", "''")
            values += f' {quote}{value}{quote}, '

        columns.append( 'last_updated_at , raw_json')
        json_str = json.dumps(payload[0],ensure_ascii=False).replace("'", "''")
        values += f' { int(time.time()) }, \' { json_str } \' '
        #values = values[:-2]
        
        sql = f'INSERT INTO {group_table_name} ( {", ".join(columns) } ) VALUES ( { values } );'    
        return sql
        
def createEventInsertStmt():
    with open('./events/group-events.json') as json_file:
        payload = json.load(json_file)
        event = payload[-1]
        all_fields = [list(event.keys())][0]
        columns = [x for x in all_fields if x not in event_fields_to_ignore]

        # add columns for structures to flatten, prefixed by the entry name
        for f in event_fields_to_flatten:
            additional_columns = [ f + '_' + c for c in [list(event[f].keys())][0] ]
            columns += additional_columns

        values = ''
        for c in columns:
            quote = ""
            if c in event:
                # top level field
                value = event[c]
            else:
                # flattened field 
                fields = c.split('_', 1)
                value = event[ fields[0] ][ fields[1] ]
                
            # insert quotes before and after String    
            if type(value).__name__ == 'str':
                quote = "'"
                value = value.replace("'", "''")
                
            values += f' {quote}{value}{quote}, '

        columns.append( 'last_updated_at , raw_json')
        json_str = json.dumps(payload[0],ensure_ascii=False).replace("'", "''")
        values += f' { int(time.time()) }, \' { json_str } \' '
        #values = values[:-2]
        
        sql = f'INSERT INTO {event_table_name} ( {", ".join(columns) } ) VALUES ( { values } );'    
        return sql        
        
if __name__ == "__main__":
    secret = db_connection.pgDSN(region_name="eu-west-3", secret_name="meetupcrawlerdatabaseSecret-IotH2oBYYAAG")

    con = None 
    
    try:
        con = psycopg2.connect(**secret)
        cur = con.cursor()
        
        print("----- Create Table -----")
        createSQL = createGroupTable()
        # createSQL = createEventTable()
        print(createSQL)
        #cur.execute(createSQL)
        
        print("----- Insert 1 row -----")
        #insertSQL = createGroupInsertStmt()
        #insertSQL = createEventInsertStmt()
        #print(insertSQL)
        #cur.execute(insertSQL)
        
        cur.close()
        con.commit()
    except psycopg2.DatabaseError as e:
        print(e)
    finally:
        if con is not None:
            con.close()