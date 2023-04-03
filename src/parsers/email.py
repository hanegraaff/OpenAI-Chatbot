import email
import logging
import base64
from email_reply_parser import EmailReplyParser

log = logging.getLogger()

class EmailMessage():
    
    def __init__(self, ses_event):
        def base64decode(msg):
            try:
                return base64.b64decode(msg).decode("utf-8")
            except:
                return msg.decode("utf-8")

        try:
            mail_dict = ses_event["mail"]

            self.sent_from = mail_dict["source"]
            self.sent_to = mail_dict["destination"][0]
            self.subject = mail_dict.get("commonHeaders", {}).get("subject", "")

            content = base64decode(ses_event["content"])
        except Exception as e:
            log.error("Error parsing SES Payload")
            log.error(ses_event)
            raise e
        
        msg = email.message_from_string(content)

        self.content_type = msg.get_content_type()
        self.is_multipart = msg.is_multipart()

        message_obj = email.message_from_string(content)

        log.info("Parsing email body")

        if self.is_multipart:
            self.body = ""

            for part in message_obj.walk():
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)

                log.debug("Next found content type: %s" % content_type)
                
                if content_type == "text/plain":
                    self.body = base64decode(payload)
                    break

        else:
            log.info("Processing Text email")
            self.body = base64decode(message_obj.get_payload(decode=True))

        if self.body == "":
            raise Exception("Could not extract body from the email message")

        log.info("Extracting latest fragment (message) from email thread")
        parsed_message = EmailReplyParser.read(self.body)
        log.info("Found: %d fragments in this email" % len(parsed_message.fragments))

        if len(parsed_message.fragments) == 0:
            log.error("Could not parse email thread. No fragments found")
            raise Exception("Could not parse email thread")
    
        self.latest_message = parsed_message.fragments[0].content

        log.info(self)

    def __str__(self):

        msg_pros = {
            "SentFrom" : self.sent_from,
            "SentTo" : self.sent_to,
            "Subject" : self.subject,
            "ContentType" : self.content_type,
            "IsMultiPart" : self.is_multipart,
            "MessageBody" : self.body,
            "Latest Message" : self.latest_message
        }

        return str(msg_pros)
        