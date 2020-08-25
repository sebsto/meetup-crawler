import os
import json
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

    def members(self, group):
        self.logger.debug(f'meetup.members for group : {group}')
        group_info = self.client.GetGroup({'urlname': group}) # pylint: disable=no-member
        return group_info.initial_data[0]

