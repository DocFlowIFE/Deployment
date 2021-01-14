import boto3
import json
import logging

import database
from database import Ticket

logger = logging.getLogger(__name__)

logger.info('Before handler')

def handler(event, context):
    client = boto3.client('secretsmanager', region_name='us-east-1')

    dbs = database.initialize_database()

    tickets = dbs.query(Ticket)
    ticket_ids = [ticket.id for ticket in tickets]
    
    return {
        "statusCode": 200,
        "body": json.dumps(
            ticket_ids
        ),
    }

