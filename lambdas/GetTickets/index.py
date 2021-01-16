import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

import database
from database import Ticket, User

logger = logging.getLogger(__name__)

logger.info('Before handler')

BUCKET_NAME = os.environ['BUCKET_NAME']

EXPIRATION_TIME = 3600

def handler(event, context):
    username = event['requestContext']['authorizer']['claims']['cognito:username']

    dbs = database.initialize_database()
    own_tickets = dbs.query(Ticket).filter(Ticket.ticket_issuer_id == User.user_id)\
                               .filter(User.email == username)
    assigned_tickets = dbs.query(Ticket).filter(Ticket.current_user_id == User.user_id)\
                               .filter(User.email == username)
    tickets = own_tickets.union(assigned_tickets)
    tickets_info = []
    s3_client = boto3.client('s3')
    for ticket in tickets:
        info = {
            "ticketId": ticket.ticket_id,
            "currentUserId": ticket.current_user_id,
            "ticketIssuerId": ticket.ticket_issuer_id,
            "dateIssued": ticket.date_issued,
            "status": ticket.status,
            "comment": ticket.comment,
        }
        key = f"{ticket.ticket_id}.pdf"
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=key)
        except ClientError:
            pass
        else:
            try:
                info["fileLink"] = s3_client.generate_presigned_url('get_object',
                                                              Params={'Bucket': BUCKET_NAME,
                                                                      'Key': key},
                                                              ExpiresIn=EXPIRATION_TIME)
            except ClientError as e:
                logging.error(e)
                return None
        tickets_info.append(info)
    
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        "body": json.dumps(
            tickets_info
        ),
    }

