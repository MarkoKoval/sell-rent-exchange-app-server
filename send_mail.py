import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import pickle
#subscriber_name = "",coursename = "",subject = "",  message = "",
def   send_email_for_course_subscription(reciever_email = "johnsmithuk08@gmail.com"):
    try:
        t = time.time()
        email = 'johnsmithuk08@gmail.com'
        password = 'johnsmith1999uk'
        send_to_email = reciever_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        with open('data.pickle', 'wb') as f:
            pickle.dump(server, f)
        print(time.time() - t)
        subject = 'New '  # The subject line
        message = "hello"

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = send_to_email
        msg['Subject'] = subject

        # Attach the message to the MIMEMultipart object
        msg.attach(MIMEText(message, 'plain'))

        text = msg.as_string()  # You now need to convert the MIMEMultipart object to a string to send
        server.sendmail(email, send_to_email, text)
        server.quit()
        print(time.time() - t)
    except Exception as e:
        print(e)

send_email_for_course_subscription()