from datetime import datetime
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
    status = parameters['status']
    comment = parameters['comment']
    ticket_id = event['pathParameters']['ticketId']
    user_email = event['requestContext']['authorizer']['claims']['cognito:username']

    dbs = database.initialize_database()
    s3_client = boto3.client('s3')
    print(ticket_id, user_email)


    ticket = dbs.query(Ticket).filter(Ticket.ticket_id == int(ticket_id))\
                                .filter(Ticket.current_user_id == User.user_id)\
                                .filter(User.email == user_email).first()

    if not ticket:
        print("No such ticket")
        return {"statusCode": 400}

    ticket.comment = comment
    if status == "rejected":
        print("rejected")
        return {"statusCode": 200}

    print(ticket.ticket_temp_id)
    templates = dbs.query(TicketTemplate)
    for template in templates:
        print(template.ticket_template_id)

    ticket_template = dbs.query(TicketTemplate).filter(TicketTemplate.ticket_template_id == ticket.ticket_temp_id).first()
    assigned_users = [user.user_id for user in list(ticket_template.users)]

    file_link = s3_client.generate_presigned_post(BUCKET_NAME,
                                                  f"{ticket.ticket_id}.pdf",
                                                  ExpiresIn=3600)

    # previous_user_email = dbs.query(TicketTemplate.email).filter(TicketTemplate.ticket_template_id == ticket.current_user_id).first()
    # print(previous_user_email, assigned_users)
    previous_user_index = assigned_users.index(ticket.current_user_id)
    if previous_user_index == len(assigned_users) - 1:
        ticket.status = "accepted"
        ticket.current_user_id = None
    else:
        ticket.current_user_id = assigned_users[previous_user_index + 1]
    dbs.commit()

    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        "body": json.dumps({
            "fileLink": file_link
        }),
    }
