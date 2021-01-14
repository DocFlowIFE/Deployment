import json
import logging

import database
from database import Ticket, TicketTemplate

logger = logging.getLogger(__name__)

logger.info('Before handler')

def handler(event, context):
    print(dir(event), event.keys())
    parameters = json.loads(event['body'])
    ticket_template_id = parameters['ticketTemplateId']



    ticket_template = dbs.query(TicketTemplate).filter(TicketTemplate.id == ticket_template_id)

    ticket = Ticket()
    ticket.ticket_temp_id = ticket_template_id
    ticket.current_user_id = ticket_template.users[0]
    ticket.status = 'pending'

    logger.info('Before return')

    return {
        "statusCode": 200,
        "body": json.dumps({}),
    }
