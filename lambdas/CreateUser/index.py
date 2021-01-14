import logging

import database
from database import User

logger = logging.getLogger(__name__)

logger.info('Before handler')

def handler(event, context):
    dbs = database.initialize_database()

    user = User(user_id=event['request']['userAttributes']['sub'], email=event['request']['userAttributes']['email'])
    dbs.add(user)
    dbs.commit()

    return event

