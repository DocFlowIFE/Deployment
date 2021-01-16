import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

import database
from database import Ticket, TicketTemplate

logger = logging.getLogger(__name__)

BUCKET_NAME = os.environ['BUCKET_NAME']
EXPIRATION_TIME = 3600

def handler(event, context):
    dbs = database.initialize_database()
    query = dbs.query(TicketTemplate)
    s3_client = boto3.client('s3')
    for template in query:
        print(template.ticket_template_id, template.filename)
    try:
        ticket_templates = [{
            "id": ticket.ticket_template_id,
            "fileLink": s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': ticket.filename},
                                                    ExpiresIn=EXPIRATION_TIME),
            "users": [user.email for user in ticket.users],
        } for ticket in query]
    except ClientError as e:
        logging.error(e)
        return None
    print(ticket_templates)
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        "body": json.dumps(
            ticket_templates
        ),

    }
