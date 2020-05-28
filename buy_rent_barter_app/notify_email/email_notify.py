import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time



def   send_email(subject = "",message = "" ,
                                         reciever_email = ""):
    print(time.time())
    email = 'johnsmithuk08@gmail.com'
    password = 'johnsmith1999uk'
    send_to_email = reciever_email
    print(subject)
    print(message)
   # subject = 'New '  # The subject line
   # message = "hello"

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject

    # Attach the message to the MIMEMultipart object
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()  # You now need to convert the MIMEMultipart object to a string to send
    server.sendmail(email, send_to_email, text)
    server.quit()
    print(time.time())
"""
t = time.time()

for i in range(100):
    send_email_for_course_subscription()
    print(str(i)+' ' + str(time.time() - t))
print(time.time() - t)
"""