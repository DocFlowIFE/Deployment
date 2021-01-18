import json
import logging
import os

import boto3

import database
from database import Ticket, TicketTemplate, User

logger = logging.getLogger(__name__)

BUCKET_NAME = os.environ['BUCKET_NAME']

def handler(event, context):
    parameters = json.loads(event['body'])
    dbs = database.initialize_database()

    users = []
    for username in parameters['users']:
        queried_user = dbs.query(User).filter(User.email == username).first()
        if not queried_user:
            return 400
        users.append(queried_user)
    ticket_template = TicketTemplate(users=users, filename=parameters['filename'], title=parameters['title'],
                                     description=parameters['description'])

    dbs.add(ticket_template)
    dbs.commit()
    s3_client = boto3.client('s3')
    file_link = s3_client.generate_presigned_post(BUCKET_NAME,
                                                 f'{ticket_template.ticket_template_id}/{parameters["filename"]}',
                                                 ExpiresIn=3600)
    print(file_link)
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        "body": json.dumps({
            "ticketTemplateId": ticket_template.ticket_template_id,
            "fileUploadLink": file_link,
        }),
    }
