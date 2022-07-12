import logging
from email_ai import lambda_handler
from ses_events.multipart_alt_sample import sns_event

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')

if __name__ == "__main__":
    lambda_handler(sns_event, None)