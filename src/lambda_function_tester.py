import logging
from lambda_handlers.email_ai import lambda_handler
from test.sns_events.reply_text_plain import sns_event
#from test.sns_events.message_multipart_alternative import sns_event

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')

if __name__ == "__main__":
    lambda_handler(sns_event, None)