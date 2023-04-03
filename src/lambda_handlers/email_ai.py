import json
import boto3
import logging
import os
import openai
import datetime
from parsers.email import EmailMessage
from email_reply_parser import EmailReplyParser

ses_client = boto3.client('ses')

log = logging.getLogger()
log.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        log.info(event)
        
        email_msg = None

        '''ses_event = json.loads(event['Records'][0]['Sns']['Message'])
        email_msg = EmailMessage(ses_event)
        '''


        response = openai.ChatCompletion.create(
            engine="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "write me some comedy in the style of Louie CK"}],
        )

        log.info("Choices: [%d]" % len(response.choices))
        log.info("Finish Reason: [%s]" %
                 response.choices[0].get("finish_reason", ""))

        openai_response = response.choices[0].get("text", "")

        response = "%s \r\n\r\n====================\r\n\r\nOn %s %s asked: \r\n %s" % (
            openai_response, datetime.datetime.now().strftime("%b %d, %Y, at %H:%M %p (UTC)"), email_msg.sent_from, email_msg.body)

        log.info("Email Response:\n%s" % response)

        #send_email(email_msg.sent_from, "RE:%s" % email_msg.subject, response)
        
        send_email("hanegraaff@gmail.com", "RE:%s" % email_msg.subject, response)
        
       

    except Exception as e:
        log.error(e)
        if email_msg is not None:
            send_email(email_msg.sent_from, "RE:%s" %
                       email_msg.subject, "Oh nose! There was an error: %s" % e)
        raise e


def send_email(email_to: str, subject: str, body: str):

    response = ses_client.send_email(
        Source='ask@hal-9001.com',
        Destination={
            'ToAddresses': [
                email_to
            ]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': body,
                }
            }
        }
    )

    log.info("resonse from ses is: %s" % response)
