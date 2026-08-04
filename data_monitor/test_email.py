import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging
import yaml

def send_alert_email(subject, body):
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        mail_cfg = config["email"]

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg['From'] = mail_cfg['sender']
        msg['To'] = mail_cfg['receiver']

        # ✅ SSL连接（465端口）不需要starttls()
        server = smtplib.SMTP_SSL(mail_cfg["smtp_server"], mail_cfg["smtp_port"])
        server.login(mail_cfg["username"], mail_cfg["password"])
        server.sendmail(mail_cfg['sender'], [mail_cfg['receiver']], msg.as_string())
        server.quit()
        logging.info("告警邮件发送成功")
    except Exception as e:
        logging.error("邮件发送失败", exc_info=True)


send_alert_email("测试告警邮件", "这是一封用于测试的邮件")