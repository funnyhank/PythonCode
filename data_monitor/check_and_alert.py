# 检查蜀都中心的网关数据写入数据库的情况


import pymysql
import yaml
import logging
import logging.config
import smtplib
from email.mime.text import MIMEText
import os

# ---------- 加载配置 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

with open(os.path.join(BASE_DIR, "logging.yaml"), "r", encoding="utf-8") as f:
    logging.config.dictConfig(yaml.safe_load(f))

logger = logging.getLogger(__name__)

# ---------- 邮件函数 ----------


def send_alert_email(subject, body):
    mail_cfg = config["email"]
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = mail_cfg['sender']
    msg['To'] = mail_cfg['receiver']
    msg['Subject'] = subject

    try:
        server = smtplib.SMTP_SSL(
            mail_cfg['smtp_server'],
            mail_cfg['smtp_port'])
        # server.starttls()
        server.login(mail_cfg['username'], mail_cfg['password'])
        server.send_message(msg)
        server.quit()
        logger.info("邮件发送成功")
    except Exception as e:
        logger.exception("邮件发送失败")

# ---------- 检查函数 ----------


def check_data_write():
    interval = config["check"]["interval_minutes"]
    expected = config["check"]["expected_count"]
    sql_path = os.path.join(BASE_DIR, "sql/check_dailydata_sdzx.sql")

    with open(sql_path, "r", encoding="utf-8") as f:
        query = f.read()

    try:
        conn = pymysql.connect(
            host=config["mysql"]["host"],
            port=config["mysql"]["port"],
            user=config["mysql"]["user"],
            password=config["mysql"]["password"],
            db=config["mysql"]["database"],
            charset="utf8mb4"
        )
        with conn.cursor() as cursor:
            cursor.execute(query, {'interval': interval})
            result = cursor.fetchone()
            count = result[0]
            logger.info(f"{interval}分钟内记录数：{count}")

            if count < expected:
                msg = f"告警：数据库表dailydata_sdzx在过去{
                    interval}分钟内仅写入{count}条数据，可能写入中断！"
                logger.warning(msg)
                send_alert_email("数据库写入告警", msg)
            else:
                logger.info("数据写入正常")
        conn.close()
    except Exception as e:
        logger.exception("数据库检查失败")


# ---------- 主程序入口 ----------
if __name__ == "__main__":
    check_data_write()
