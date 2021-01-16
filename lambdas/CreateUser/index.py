import logging

import database
from database import User

logger = logging.getLogger(__name__)

logger.info('Before handler')

def handler(event, context):
    dbs = database.initialize_database()

    query = dbs.query(User).filter(User.email == event['request']['userAttributes']['email']).first()
    print(dbs.query(User).count())
    if query:
        print("exists")
        return event
    user = User(email=event['request']['userAttributes']['email'])
    dbs.add(user)
    print("not committed", user.user_id, user.email)
    dbs.commit()
    print("committed", user.user_id, user.email)

    return event

