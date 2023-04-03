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

        #log.info(event)
        
        email_msg = None

        '''ses_event = json.loads(event['Records'][0]['Sns']['Message'])
        email_msg = EmailMessage(ses_event)
        
        '''
        
        question = '''
            Summarize this article: 
                
                Leaks From Bragg's Grand Jury Are A Crime
        
                Tyler Durden's Photo
                BY TYLER DURDEN
                SUNDAY, APR 02, 2023 - 07:00 PM
                Authored by Alan Dershowitz via New York Sun,
                
                The protection of secrecy is as applicable to President Trump as it is to anyone else...
                
                
                
                
                Recommended Videos
                
                Wall St ends year with biggest annual drop since 2008
                17.3M
                99
                Upstart
                Borrow Now
                Etoro
                Invest Now
                
                
                Ad: (2)
                Skip Ad
                Wall St ends year with biggest annual drop since 2008NOW PLAYING
                'Far more bullish than most people' on 2023 -CIO
                Bond selloff 'unambiguously bad for all assets' -CIO
                Huawei: 'business as usual' as U.S. sanctions pain ebbs
                Africa in Business: China's COVID risk on S. Africa rand
                Chinese airlines to win big on border opening
                The Year in Numbers: rising prices, endless Elon
                Southwest promises refunds over snow chaos
                It is likely that a serious felony has been committed right under District Attorney Alvin Bragg’s nose and he is not investigating it. Under New York law, it is a felony to leak confidential grand jury information, such as whether the jurors voted to indict. The protection of secrecy is as applicable to President Trump as it is to anyone else. 
                
                We know that the information was disclosed while the indictment itself remains sealed and before any official announcement was made or charges brought. It is unlikely that the leak came from the Trump team, which seemed genuinely surprised.
                
                The most likely, though uncertain, scenario is that a person in Mr. Bragg’s office or a grand juror unlawfully leaked the sealed information. That would be a class E felony, subject to imprisonment.
                
                It is possible of course that an investigation is underway, but it seems more likely that Mr. Bragg is too busy making up a crime against the man he promised in his campaign to get than investigating a real crime that took place on his watch.
                
                In my new book, “Get Trump,” I predicted that partisan prosecutors would try to get Trump regardless of the lack of evidence or law. That prediction has come true. Since the indictment itself has not been leaked — at least not yet — we don’t know its specifics. We do know, based on leaks, that it involves multiple counts, almost certainly involving the payment of hush money to a porn actress.
                
                
                
                Under Mr. Bragg’s likely theory, Mr. Trump should have disclosed in his public corporate records that he paid the hush money to avoid his adulterous affair from becoming public. But no one in history has ever publicly disclosed the reason he paid money for a non-disclosure agreement.
                
                Why would Mr. Trump pay the money in the first place if he had to publicly disclose the embarrassing reason? Furthermore, no one in history has ever been indicted for listing “legal expenses” for setting a potentially embarrassing payment of hush money.
                
                Thus, even the misdemeanor allegation involving false entries is unprecedented and represents selective prosecution. It is also almost certainly barred by the two-year statute of limitations. In order to elevate this bookkeeping case into a felony, Mr. Bragg must also prove beyond a reasonable doubt that the reason Trump made the false entry — if he himself did it — was solely as a campaign contribution to help him win his election.
                
                If Mr. Trump was motivated in part by his desire to protect his wife, children, and business interests from harmful disclosures, that would not constitute the crime of making an undisclosed campaign contribution. So this too is a stretch.
                
                It is a fundamental tenet of American law that criminal law should not be stretched to fit targeted defendants. Criminal statutes must be clear and unambiguous. If there is any doubt, the age-old concept of “lenity” requires that these doubts be resolved in favor of the defendant.
                
                Thomas Jefferson once quipped that for a criminal statute to be valid, it must be so clear that a reasonable person could understand it if he read it “while running.” A nice image!
                
                I intend to read the text of the indictment, while sitting, with 60 years of experience behind me. I doubt I will find that it meets the constitutional criteria for “fair warning,” although I maintain an open mind until I have studied it carefully.
                
                The important point is that when a district attorney ran for office as a Democrat pledging to get Mr. Trump, who is a candidate for president against the incumbent Democrat, that district attorney must have an airtight case.
                
                A weak, questionable, unprecedented, and novel stitching together of two inapplicable statutes, will not, and should not, satisfy the American public that this is not a partisan targeting of a political opponent.
                
        '''

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "%s" % (question)}],
        )
        
        #log.info("Response: %s" % (response))

        log.info("Choices: [%d]" % len(response.choices))
        log.info("Finish Reason: [%s]" %
                 response.choices[0].get("finish_reason", ""))

        openai_response = response.choices[0].get("message", {}).get("content", "")

        '''response = "%s \r\n\r\n====================\r\n\r\nOn %s %s asked: \r\n %s" % (
            openai_response, datetime.datetime.now().strftime("%b %d, %Y, at %H:%M %p (UTC)"), email_msg.sent_from, email_msg.body)
        '''
            
        response = "Question on %s: %s \r\n\Answer:%s \r\n" % ( 
            datetime.datetime.now().strftime("%b %d, %Y, at %H:%M %p (UTC)"),
            question,
            openai_response)
  
            

        log.info("Email Response:\n%s" % response)

        #send_email(email_msg.sent_from, "RE:%s" % email_msg.subject, response)
        

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
