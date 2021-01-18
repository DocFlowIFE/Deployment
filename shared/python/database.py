import json
import os

import boto3
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Table, ForeignKey, Integer, String, ARRAY
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_NAME = os.environ['RDS_Database']
RDS_HOST = os.environ['RDS_HOST']
RDS_PORT = os.environ['RDS_PORT']
SECRET_ARN = os.environ['RDS_SECRET_ARN']
Base = declarative_base()

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

    title = Column(String(1000))
    filename = Column(String(100))
    description = Column(String(1000))
    users = relationship("User", secondary=user_ticket_templates)


class Ticket(Base):
    __tablename__ = 'ticket'
    ticket_id = Column(Integer, primary_key=True)

    filename = Column(String(100))

    # FK many-to-one Ticket-TicketTemplate
    ticket_temp_id = Column(Integer, ForeignKey('ticket_template.ticket_template_id'))

    # FK many-to-one Ticket-User
    current_user_id = Column(Integer, ForeignKey('user.user_id'))

    ticket_issuer_id = Column(Integer, ForeignKey('user.user_id'))

    date_issued = Column(String(100))
    status = Column(String(100))
    comment = Column(String(1000))

def initialize_database():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=SECRET_ARN)
    data = json.loads(response['SecretString'])
    username = data['username']
    password = data['password']

    engine = sqlalchemy.create_engine(f'mysql+pymysql://{username}:{password}@'
                                      f'{RDS_HOST}:{RDS_PORT}/{DATABASE_NAME}').connect()
    Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine)
    return session()
