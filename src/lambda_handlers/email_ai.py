import json
import boto3
import logging
import os
import openai
from parsers.email import EmailMessage
from email_reply_parser import EmailReplyParser

ses_client = boto3.client('ses')

log = logging.getLogger()
log.setLevel(logging.INFO)

def lambda_handler(event, context):

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        log.info(event)
        
        ses_event = json.loads(event['Records'][0]['Sns']['Message'])

        email_msg = None
        email_msg = EmailMessage(ses_event)



        '''if email_msg.subject.lower().startswith("fw:") or email_msg.subject.lower().startswith("fwd:"):
            pass
        else:
            pass
        '''

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=email_msg.latest_message,
            temperature=0.7,
            max_tokens=250,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            echo=False,
            best_of=3
            )

            
        print("Choices: [%d]" % len(response.choices))
        print("Finish Reason: [%s]" % response.choices[0].get("finish_reason", ""))
        
        openai_response = response.choices[0].get("text", "")
        print("Response:\n%s" % openai_response)
        
        
        send_email(email_msg.sent_from, "RE:%s" % email_msg.subject, openai_response)

    except Exception as e:
        log.error(e)
        if email_msg is not None:
            send_email(email_msg.sent_from, "RE:%s" % email_msg.subject, "Oh nose! There was an error: %s" % e)
        raise e


def send_email(email_to : str, subject : str, body : str):
    
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
