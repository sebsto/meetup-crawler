import json
import time

import db_connection
import psycopg2

table_name = 'meetup_group'
fields_to_ignore=['organizer', 'who', 'group_photo', 'key_photo', 'category', 'meta_category']
type_association={ 'str' : 'VARCHAR', 'bool' : 'BOOLEAN', 'int' : 'BIGINT', 'float' : 'NUMERIC'}

def createDBSchema():
    with open('./events/group-info.json') as json_file:
        payload = json.load(json_file)
        group = payload[0]
        all_fields = [list(x.keys()) for x in payload][0]
        columns = [x for x in all_fields if x not in fields_to_ignore]
    
        field_list = ''
        for c in columns:
            # { (" PRIMARY KEY" if c == "id" else "") } not using PK because 
            field_list += f'{c} {type_association[type(group[c]).__name__]}, '
            
        field_list += 'last_updated_at BIGINT, raw_json JSON NOT NULL'  
        #field_list = field_list[:-2]

        sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({field_list});'
        return sql

def createInsertStmt():
    with open('./events/group-info.json') as json_file:
        payload = json.load(json_file)
        group = payload[0]
        all_fields = [list(x.keys()) for x in payload][0]
        
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
        json_str = json.dumps(payload[0],ensure_ascii=False).replace("'", "''")
        values += f' { int(time.time()) }, \' { json_str } \' '
        #values = values[:-2]
        
        sql = f'INSERT INTO {table_name} ( {", ".join(columns) } ) VALUES ( { values } );'    
        return sql
        
if __name__ == "__main__":
    secret = db_connection.pgDSN(region_name="eu-west-3", secret_name="meetupcrawlerdatabaseSecret-IotH2oBYYAAG")

    con = None 
    
    try:
        con = psycopg2.connect(**secret)
        cur = con.cursor()
        
        print("----- Create Table -----")
        createSQL = createDBSchema()
        print(createSQL)
        cur.execute(createSQL)
        
        print("----- Insert 1 row -----")
        insertSQL = createInsertStmt()
        print(insertSQL)
        cur.execute(insertSQL)
        
        cur.close()
        con.commit()
    except psycopg2.DatabaseError as e:
        print(e)
    finally:
        if con is not None:
            con.close()