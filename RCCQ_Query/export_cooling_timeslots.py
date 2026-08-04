#用于导出蜀都上一月的整点数据

import pandas as pd
import pymysql
import yaml
import logging
import logging.config
from datetime import datetime, timedelta
import os

# ---------- 设置目录 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- 加载日志 ----------
with open(os.path.join(BASE_DIR, "logging.yaml"), "r", encoding="utf-8") as f:
    logging_config = yaml.safe_load(f)
    logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)

# ---------- 加载数据库配置 ----------
with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

db_config = {
    "host": config["mysql"]["host"],
    "port": config["mysql"]["port"],
    "user": config["mysql"]["user"],
    "password": config["mysql"]["password"],
    "db": config["mysql"]["database"],
    "charset": "utf8mb4"
}

# ---------- 获取上月起止时间 ----------
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
last_day_last_month = first_day_this_month - timedelta(days=1)
first_day_last_month = datetime(last_day_last_month.year, last_day_last_month.month, 1)

start_date = first_day_last_month.strftime('%Y-%m-%d')
end_date = last_day_last_month.strftime('%Y-%m-%d')

# ---------- 查询上月数据 ----------
sql = f"""
SELECT Timestamp, Tag, Value
FROM dailydata_sdzx
WHERE Timestamp BETWEEN '{start_date} 00:00:00' AND '{end_date} 23:59:59'
AND Tag IN ('1期累计冷量', '2期累计冷量','1期供水温度','1期回水温度','1期流量','2期供水温度','2期回水温度','2期流量')
"""
# sql =f"""
# # SELECT Timestamp, Tag, Value
# #             FROM dailydata_sdzx
# #             WHERE Tag IN ('1期累计冷量', '2期累计冷量','1期供水温度','1期回水温度','1期流量','2期供水温度','2期回水温度','2期流量')
# #             AND Timestamp >= '{start_str}' AND Timestamp < '{end_str}'
# #             AND TIME(Timestamp) IN ({','.join([f"'{t}'" for t in TIMES])})"""
try:
    conn = pymysql.connect(**db_config)
    df = pd.read_sql(sql, conn)
    conn.close()
    logger.info(f"读取数据成功，记录数：{len(df)}")
except Exception as e:
    logger.exception("读取数据库失败")
    raise e

# ---------- 数据预处理 ----------
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Date'] = df['Timestamp'].dt.date
df['Time'] = df['Timestamp'].dt.time

# 目标时间点
target_times = ['00:00:00', '08:00:00', '18:00:00', '22:00:00']
target_times = [datetime.strptime(t, "%H:%M:%S").time() for t in target_times]

# 构造结果字典
results = {
    '1期累计冷量': pd.DataFrame(index=pd.date_range(start=start_date, end=end_date).date),
    '2期累计冷量': pd.DataFrame(index=pd.date_range(start=start_date, end=end_date).date)
}

for tag in ['1期累计冷量', '2期累计冷量']:
    for t in target_times:
        filtered = df[(df['Tag'] == tag) & (df['Time'] == t)]
        temp_series = filtered.set_index('Date')['Value'].round(0).astype('Int64')
        col_label = t.strftime("%H:%M")
        results[tag][col_label] = temp_series

# 重命名 index 为日期
for tag_df in results.values():
    tag_df.index.name = '日期'

# ---------- 写入 Excel ----------
output_path = os.path.join(BASE_DIR, f"冷量时点数据_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    results['1期累计冷量'].to_excel(writer, sheet_name='1期累计冷量')
    results['2期累计冷量'].to_excel(writer, sheet_name='2期累计冷量')

logger.info(f"写入 Excel 成功：{output_path}")
print(f"✅ 已导出文件：{output_path}")
