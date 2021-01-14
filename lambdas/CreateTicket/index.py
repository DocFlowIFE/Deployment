import json
import logging

import database
from database import TicketTemplate

logger = logging.getLogger(__name__)

def handler(event, context):
    print(event)
    print(context)
    parameters = json.loads(event['body'])
    ticket_template_id = parameters['ticketTemplateId']

    dbs = database.initialize_database()

    ticket_template = dbs.query(TicketTemplate).filter(TicketTemplate.id == ticket_template_id)

    ticket = TicketTemplate()
    ticket.ticket_temp_id = ticket_template_id
    ticket.current_user_id = ticket_template.users[0]
    ticket.status = 'pending'

    return {
        "statusCode": 200,
        "body": json.dumps({}),
    }
