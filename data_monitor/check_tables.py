## 检查RCCQ和IUDC写入数据库的情况

import pymysql
import yaml
import logging.config
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os

# 初始化日志
with open("logging.yaml", 'r', encoding='utf-8') as f:
    logging.config.dictConfig(yaml.safe_load(f))
logger = logging.getLogger()

# 加载配置
with open("config1.yaml", 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

db_cfg = config['database']
mail_cfg = config['mail']

# 读取 SQL 文件


def load_sql(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# 发送邮件
def send_alert_email(missing_tables):
    msg = EmailMessage()
    msg['Subject'] = f"[报警] 数据表未写入（{datetime.now().date()}）"
    msg['From'] = mail_cfg['from']
    msg['To'] = ', '.join(mail_cfg['to'])
    msg.set_content(f"以下数据表在今天未检测到数据写入：\n\n" + "\n".join(missing_tables))

    try:
        server = smtplib.SMTP_SSL(mail_cfg['smtp_server'], mail_cfg['smtp_port'])
        if mail_cfg.get('use_tls'):
            server.starttls()
        server.login(mail_cfg['username'], mail_cfg['password'])
        server.send_message(msg)
        server.quit()
        logger.info("邮件发送成功")
    except Exception as e:
        logger.error("邮件发送失败", exc_info=e)


# 检查表


def check_table(conn, table_name, sql_file):
    sql = load_sql(sql_file)
    with conn.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchone()
        logger.info(f"{table_name} 今日记录数：{result[0]}")
        return result[0] > 0


def main():
    missing_tables = []
    try:
        conn = pymysql.connect(**db_cfg)
        tables_to_check = {
            'dailydata_iudc': 'sql/check_dailydata_iudc.sql',
            'dailydata_rccq': 'sql/check_dailydata_rccq.sql'
        }

        for table_name, sql_path in tables_to_check.items():
            if not check_table(conn, table_name, sql_path):
                missing_tables.append(table_name)

        if missing_tables:
            logger.warning(f"缺失数据的表：{missing_tables}")
            send_alert_email(missing_tables)
        else:
            logger.info("所有表数据写入正常")

    except Exception as e:
        logger.error("程序运行出错", exc_info=e)
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()
