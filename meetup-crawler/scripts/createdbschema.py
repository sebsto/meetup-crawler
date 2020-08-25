import json

table_name = 'meetup_group'
fields_to_ignore=['organizer', 'who', 'group_photo', 'key_photo', 'category', 'meta_category']
type_association={ 'str' : 'VARCHAR', 'bool' : 'BOOLEAN', 'int' : 'BIGINT', 'float' : 'NUMERIC'}

with open('./events/group-info.json') as json_file:
    payload = json.load(json_file)
    group = payload[0]
    all_fields = [list(x.keys()) for x in payload][0]
    columns = [x for x in all_fields if x not in fields_to_ignore]

    field_list = ''
    for c in columns:
        field_list += f'{c} {type_association[type(group[c]).__name__]}{ (" PRIMARY KEY" if c == "id" else "") }, '
    field_list = field_list[:-2]

    sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({field_list});'
    print(sql)