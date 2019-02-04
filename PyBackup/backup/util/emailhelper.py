import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header

class EmailHelper(object):
    def __init__(self,host,username,password,port = 25,is_ssl = False):
        if is_ssl:
            self.smtp = smtplib.SMTP_SSL(host, port)
        else:
            self.smtp = smtplib.SMTP(host,port)
        self.username = username
        self.smtp.login(username,password)
    def send(self,to_name,subject,content,receivers = [],filepath = []):
        message = MIMEMultipart()
        message['From'] = formataddr(['新的备份',self.username])
        message['To'] = to_name
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        for file in filepath:
            att = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename="{0}"'.format(os.path.basename(file))
            message.attach(att)
        try:
            self.smtp.sendmail(self.username, receivers, message.as_string())
            return True,'发送成功'
        except Exception as e:
            return False,str(e)
    def quit(self):
        self.smtp.quit()


