import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

"""
if  course_creator_email != None and bool(re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$",course_creator_email)):
       # re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", course_creator_email)):
        import threading
        t = threading.Thread(target=send_email_for_course_subscription, args=(username, coursename,
            'New subscriber for the course congratulations',
                                         username + " " + " subscribed to your course " + coursename ,course_creator_email
        ), kwargs={})
        t.setDaemon(True)
        t.start()
"""

def   send_email_for_course_subscription(message = "hello" ,subject = "",
                                         reciever_email = "marko.koval.pz.2016@lpnu.ua"):
    email = 'johnsmithuk08@gmail.com'
    password = 'johnsmith1999uk'
    send_to_email = reciever_email
    subject = 'New '  # The subject line
    message = "hello"

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

t = time.time()

for i in range(100):
    send_email_for_course_subscription()
    print(str(i)+' ' + str(time.time() - t))
print(time.time() - t)