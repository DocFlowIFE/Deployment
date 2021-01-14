import json
import logging

import database
from database import Ticket

logger = logging.getLogger(__name__)

def handler(event, context):
    dbs = database.initialize_database()

    tickets = dbs.query(Ticket)
    ticket_ids = [ticket.id for ticket in tickets]

    return {
        "statusCode": 200,
        "body": json.dumps(
            ticket_ids
        ),
    }

