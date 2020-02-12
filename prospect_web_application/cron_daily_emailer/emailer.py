import smtplib
import os
from datetime import datetime
from decouple import config
from email_body import EMAIL_BODY_TEMPLATE

MESSAGE_FORMAT = """MIME-Version: 1.0
Content-type: text/html
Subject: {} ALERT !!!


{}"""



def send_email(	
				client,
				email_subject,
				email_header,
				email_body,
				reciever_emails
			  ):
	'''
	##################################
	Input parameter:
	client : Name of Client 
	email_subject: Subject of the email
	email_header : Header of Email
	email_body : Body of Email
	reciever_emails: List of reciepment email addresses 
	##################################
	'''
	email_msg_body = EMAIL_BODY_TEMPLATE.format(client, email_header, email_body)

	# with open('a.html','w') as f:
	# 	f.write(email_msg_body)
	# exit(1)
	port = config('port')
	smtp_server = config('smtp_server')
	sender_email = config('sender_email')
	password = config('password')


	server = smtplib.SMTP(smtp_server, port)
	server.ehlo()
	server.starttls()
	server.login(sender_email, password)
	server.sendmail(sender_email, reciever_emails, MESSAGE_FORMAT.format(email_subject, email_msg_body))

	server.quit()

