import pymysql
import boto3
import json
import os
import sqlalchemy
import logging

dbname = os.environ['RDS_Database']
host = os.environ['RDS_HOST']
port = os.environ['RDS_PORT']
secret = os.environ['RDS_SECRET_ARN']
Base = declarative_base()

logging.info('Before handler')


class Document(Base):
    __tablename__ = 'document'
    document_id = Column(Integer, primary_key=True)
    filename = Column(String(100))
    uploaded_by = Column(Integer)

    #FK one-to-many Ticket-Document
    ticket_id = Column(Integer, ForeignKey('ticket.ticket_id'))


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    email = Column(String(100))


user_ticket_templates = Table('association', Base.metadata,
    Column('ticket_template_id', Integer, ForeignKey('ticket_template.ticket_template_id')),
    Column('user_id', Integer, ForeignKey('user.user_id'))
)


class TicketTemplate(Base):
    __tablename__ = 'ticket_template'
    ticket_template_id = Column(Integer, primary_key=True)
    tickets = relationship('Ticket', backref="ticket_template")

    filename = Column(String(100))
    description = Column(String(1000))
    users = relationship("User", secondary=user_ticket_templates)


class Ticket(Base):
    __tablename__ = 'ticket'
    ticket_id = Column(Integer, primary_key=True)

    # FK one-to-many Ticket-Document
    document_id  = relationship("Document", backref="ticket")

    # FK many-to-one Ticket-TicketTemplate
    ticket_temp_id = Column(Integer, ForeignKey('ticket_template.ticket_template_id'))

    # FK many-to-one Ticket-User
    current_user_id = Column(Integer, ForeignKey('user.user_id'))

    date_issued = Column(String(100))
    status = Column(String(100))
    comment = Column(String(1000))


def handler(event, context):

    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret)
    data = json.loads(response['SecretString'])
    username = data['username']
    password = data['password']

    logging.info('Before engine')

    engine = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(username, password, host, dbname)).connect()

    logging.info('After engine')

    Base.metadata.create_all(engine);
    
    logging.info('Before session')
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    logging.info('After session')
    
    tickets = session.query(Ticket);
    ticket_ids = [ticket.id for ticket in tickets]
    
    logging.info('Before return')
    
    return {
        "statusCode": 200,
        "body": json.dumps(
            ticket_ids
        ),
    }
