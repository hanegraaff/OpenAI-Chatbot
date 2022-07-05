import json
import boto3
import base64
import email
import logging
import os
import openai

ses_client = boto3.client('ses')


def lambda_handler(event, context):
    
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        ses_event = json.loads(event['Records'][0]['Sns']['Message'])
        
        print(ses_event)
        
        sent_from = ses_event['mail']['source']
        sent_to = ses_event['mail']['destination'][0]
        subject = ses_event['mail']['commonHeaders']['subject']
        content = base64.b64decode(ses_event['content'])
        
        message = email.message_from_string(str(content.decode("utf-8") )).get_payload()
    
    
        print("Sent From: %s" % sent_from)
        print("Sent To: %s" % sent_to)
        print("Subject: %s" % subject)
        print("Message: %s" % message)
        
        response = "this is a test"
        
        
        send_email(sent_from, "RE:%s" % subject, response)
    except Exception as e:
        print(e)
        raise e
    
    

def send_email(email_to : str, subject : str, body : str):
    
        response = ses_client.send_email(
            Source='king@kunkank.com',
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
        
        print("resonse from ses is: %s" % response)

    