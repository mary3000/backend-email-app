#!/usr/bin/env python
import pika
import time
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '<your-email>'  # FILL ME
app.config['MAIL_PASSWORD'] = '***'  # FILL ME
app.config['MAIL_DEFAULT_SENDER'] = '<your-email>'  # FILL ME
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

queue_name = 'mail_validator'

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

worker = 'Consumer: '


def callback(ch, method, properties, body):
    LOG.info(worker + "received:\t%s" % body)
    addr, token = body.split(' ')

    with app.app_context():
        msg = Message("Hello",
                      recipients=[addr])
        msg.html = "Follow <a href=\"http://0.0.0.0:8080/confirm?token=" + token + "\">this</a> link to confirm your email."
        mail.send(msg)


if __name__ == '__main__':

    time.sleep(5)

    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('rabbitmq',
                                           5672,
                                           '/',
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    channel.basic_consume(on_message_callback=callback,
                          queue=queue_name)

    LOG.info(worker + 'Waiting for messages. To exit press Ctrl+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    LOG.info(worker + 'closing connection...')
    connection.close()
