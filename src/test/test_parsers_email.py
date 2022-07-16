"""Author: Mark Hanegraaff -- 2022
    Testing class for the parsers.email module
"""

from parsers.email import EmailMessage
import unittest
import json
import test.sns_events.reply_text_plain

class TestEmailMessage(unittest.TestCase):

    def test_reply_text_plain(self):
        ses_event = json.loads(
            test.sns_events.reply_text_plain.sns_event['Records'][0]['Sns']['Message'])

        email_msg = EmailMessage(ses_event)

        self.assertEqual(email_msg.sent_from, "test@gmail.com")
        self.assertEqual(email_msg.sent_to, "ask@xxx.com")
        self.assertEqual(email_msg.subject, "Re: This is a test")
        self.assertEqual(email_msg.content_type, "text/plain")
        self.assertEqual(email_msg.is_multipart, False)
        self.assertEqual(email_msg.latest_message, "What is your name?")
