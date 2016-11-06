# Imports
from apiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from email.mime.text import MIMEText


def gmail():
	# Only need to send an email, so that's the only scope included.  Others can be added if required later.
	SCOPES = 'https://www.googleapis.com/auth/gmail.send'

	# Google API Client Secrets need to be downloaded from Google and saved as named below
	CLIENT_SECRET = '/home/pi/Projects/SendMail/client_secret.json'

	store = file.Storage('/home/pi/Projects/SendMail/storage.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
		creds = tools.run_flow(flow, store)
		
	svc = build('gmail', 'v1', http=creds.authorize(Http()))
	
	return svc

def send_mail(subject, msgIn):
	"""Send an email message.

	Args:
	  service: Authorized Gmail API service instance.
	  user_id: User's email address. The special value "me"
	  can be used to indicate the authenticated user.
	  msgIn: Message to be sent.

	Returns:
	  Sent Message.
	"""
	#message = MIMEText(msgIn)
	#message['To'] = '6029095796@tmomail.net'
	#message['From'] = 'fiffer1@gmail.com'
	#message['Subject'] = subject
	#raw = base64.urlsafe_b64encode(message.as_string())
	#print(raw)
  
	msg = CreateMessage(subject,msgIn)
	#msg = MIMEText(msgIn)
	#msg['Subject'] = subject
	#msg['From'] = 'fiffer1@gmail'
	#msg['To'] = '6029095796@tmomail.net'
	#msg = base64.urlsafe_b64encode(msg.as_string())
	
	try:
		service = gmail()
		messageOut = (service.users().messages().send(userId='me', body=msg).execute())
		#print 'Message Id: %s' % messageOut['id']
		return messageOut
	except errors.HttpError, error:
		print 'This error occurred: %s' % error
	
def CreateMessage(subject, message_text):
  """Create a message for an email.

  Args:
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = '6029095796@tmomail.net'
  message['from'] = 'fiffer1@gmail.com'
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}
