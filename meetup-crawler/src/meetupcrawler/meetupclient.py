import os
import json
import time
import logging


import meetup.api

class MeetupClient(object):
    def __init__(self):
        # Initialize logging with level provided as environment variable
        LOGLEVEL = os.environ.get('PYTHON_LOGLEVEL', 'WARNING').upper()
        NUMERIC_LOGLEVEL = getattr(logging, LOGLEVEL, None)
        if not isinstance(NUMERIC_LOGLEVEL, int):
            raise Exception(f'Invalid log level: {NUMERIC_LOGLEVEL}')

        self.logger = logging.getLogger("MeetupClient")
        self.logger.setLevel(NUMERIC_LOGLEVEL)

        self.client = meetup.api.Client()
        self.logger.debug('Meetup Client Created')

    def group(self, group):
        self.logger.debug(f'meetup.group for group : {group}')
        group_info = self.client.GetGroup({'urlname': group}) # pylint: disable=no-member
        return group_info.initial_data[0]
        
    def events(self, group, start_date=0, end_date=int(time.time())):
        start = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(start_date))
        self.logger.debug(f"meetup.events for group : { group['name'] } { ('(> ' + start + ')') if start_date > 0 else '' } ")
        
        if start_date > 0:
        # https://github.com/pferate/meetup-api/ 
        # the Python API does not support meetup API v3 GetEvents with server side filtering
        # https://github.com/pferate/meetup-api/blob/master/meetup/api_specification/meetup_v3_services.json 
        # https://secure.meetup.com/meetup_api/console/?path=/:urlname/events
            events = self.client.GetEvents({'group_id' : group['id'],
                                            'text_format' : 'plain',
                                            'status':'past'
            })
            
            # filtering here, on the client side 
            result = list(filter(lambda e : e['time']/1000 >= start_date and e['time']/1000 < end_date , events.results))

        else:
            
            events = self.client.GetEvents({'group_id' : group['id'],
                                            'text_format' : 'plain',
                                            'status':'past'})
            result = events.results
            
        return result

        

