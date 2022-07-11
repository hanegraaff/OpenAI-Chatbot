import json
import boto3
import base64
import email
import logging
import os
import openai
from email_reply_parser import EmailReplyParser
#from ses_events.multipart_alt_sample import sns_event

ses_client = boto3.client('ses')

#logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')

log = logging.getLogger()
log.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    sent_from = ""

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        ses_event = json.loads(event['Records'][0]['Sns']['Message'])
        #ses_event = json.loads(sns_event['Records'][0]['Sns']['Message'])

        
        log.info(ses_event)
        
        (sent_from, subject, message) = parse_ses_event(ses_event)

        if subject.lower().startswith("fw:") or subject.lower().startswith("fwd:"):
            prompt = handle_forward(message)
        else:
            prompt = handle_message(message)

        log.info("Extracted the following prompt: %s" % prompt)

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
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
        
        
        send_email(sent_from, "RE:%s" % subject, openai_response)

    except Exception as e:
        log.error(e)
        if sent_from != "":
            send_email(sent_from, "RE:%s" % subject, "Oh nose! There was an error: %s" % e)
        raise e
    
    

def parse_ses_event(ses_event : object): #-> tuple
    log.info("Parsing SES Email")

    sent_from = ses_event['mail']['source']
    sent_to = ses_event['mail']['destination'][0]
    subject = ses_event['mail']['commonHeaders']['subject']
    content = base64.b64decode(ses_event['content'])
    
    msg = email.message_from_string(str(content.decode("utf-8") ))
    is_multipart = msg.is_multipart()
    
    log.info("Sent From: %s" % sent_from)
    log.info("Sent To: %s" % sent_to)
    log.info("Subject: %s" % subject)
    log.info("Content Type: %s" % msg.get_content_type())
    log.info("Multipart? : %s" % is_multipart)

    message_obj = email.message_from_string(str(content.decode("utf-8") ))
    if is_multipart:
        message = ""

        for part in message_obj.walk():
            content_type = part.get_content_type()
            payload = part.get_payload()

            log.debug("Next found content type: %s" % content_type)
            
            if content_type == "text/plain":
                message = payload
                break

    else:
        message = message_obj.get_payload()

    if message == "":
        raise Exception("Could not extract text from the email message")

    return (sent_from, subject, message)


def handle_forward(message : str):
    pass

def handle_message(message : str):
    log.info("Handling a Reply to an email...")
    parsed_message = EmailReplyParser.read(message)
    log.info("Found: %d fragments in this email" % len(parsed_message.fragments))
    
    prompt = parsed_message.fragments[0].content

    return prompt

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

    
#lambda_handler(None, None)