import boto3
import logging

log = logging.getLogger()

try:
    ses_client = boto3.client('ses')
except Exception as e:
    log.error("Could not initialize AWS SES Client")
    raise e


def send_email(email_from: str, email_to: str, subject: str, body: str):

    response = ses_client.send_email(
        Source='email_from',
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
