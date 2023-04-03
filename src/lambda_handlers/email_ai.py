import json
import boto3
import logging
import os
import openai
import datetime
from parsers.email import EmailMessage
from connectors import ses

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

        log.info("Choices: [%d]" % len(response.choices))
        log.info("Finish Reason: [%s]" %
                 response.choices[0].get("finish_reason", ""))

        openai_response = response.choices[0].get("text", "")

        response = "%s \r\n\r\n====================\r\n\r\nOn %s %s asked: \r\n %s" % (
            openai_response, datetime.datetime.now().strftime("%b %d, %Y, at %H:%M %p (UTC)"), email_msg.sent_from, email_msg.body)

        log.info("Email Response:\n%s" % response)

        ses.send_email(email_msg.sent_to, email_msg.sent_from, "RE:%s" % email_msg.subject, response)

    except Exception as e:
        log.error(e)
        if email_msg is not None:
            ses.send_email(email_msg.sent_to, email_msg.sent_from, "RE:%s" %
                       email_msg.subject, "Oh nose! There was an error: %s" % e)
        raise e

