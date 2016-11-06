import smtplib
from email.mime.text import MIMEText

# https://en.wikipedia.org/wiki/List_of_SMS_gateways
# 10DigitNumber@text.att.net for AT&T
# 10DigitNumber@vtext.com for Verizon
# 10DigitNumber@tmomail.net


# Mail setup
username = 'ctreynapp'
password = '3g#y6qoMGXSe'
fromaddr = 'ctreynapp@gmail.com'
toaddrs  = '6029095796@tmomail.net'

# The actual mail send
def send_mail(subject,msgIn):
    msg = MIMEText(msgIn)
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddrs
    msg = msg.as_string()
    
    session = smtplib.SMTP('smtp.gmail.com',587)
    session.ehlo()
    session.starttls()
    session.login(username,password)
    session.sendmail(fromaddr, toaddrs, msg)
    session.quit()

#send_mail('Test Text','Test')

