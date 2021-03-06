from datetime import date
import json
import logging
import os

import boto3

import database
from database import Ticket, TicketTemplate, User

logger = logging.getLogger(__name__)

BUCKET_NAME = os.environ['BUCKET_NAME']

def handler(event, context):
    print(event)
    parameters = json.loads(event['body'])
    ticket_template_id = parameters['ticketTemplateId']
    ticket_issuer_mail = event['requestContext']['authorizer']['claims']['cognito:username']

    dbs = database.initialize_database()
    s3_client = boto3.client('s3')

    ticket_template = dbs.query(TicketTemplate).filter(TicketTemplate.ticket_template_id == ticket_template_id).first()
    ticket_issuer = dbs.query(User).filter(User.email == ticket_issuer_mail).first()

    ticket = Ticket()
    ticket.ticket_temp_id = ticket_template_id
    ticket.current_user_id = ticket_template.users[0].user_id
    ticket.ticket_issuer_id = ticket_issuer.user_id
    ticket.date_issued = str(date.today())
    ticket.status = 'pending'
    ticket.comment = parameters['comment']
    ticket.filename = parameters['filename']
    dbs.add(ticket)
    dbs.commit()
    file_link = s3_client.generate_presigned_post(BUCKET_NAME,
                                                  f"userTickets/{ticket.ticket_id}/{parameters['filename']}",
                                                  ExpiresIn=3600)
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        "body": json.dumps({
            "ticketId": ticket.ticket_id,
            "fileLink": file_link
        }),
    }
