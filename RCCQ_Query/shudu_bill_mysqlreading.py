#后续需求更新，在每个月初读取上一个月的数据

import pandas as pd
import pymysql
import yaml
import logging
import logging.config
from datetime import datetime

# ----------- 加载日志配置 -----------
with open("logging.yaml", 'r', encoding='utf-8') as log_config_file:
    log_config = yaml.safe_load(log_config_file)
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

# ----------- 加载数据库配置 -----------
with open("config.yaml", 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)

db_config = {
    'host': config['mysql']['host'],
    'port': config['mysql']['port'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password'],
    'db': config['mysql']['database'],
    'charset': 'utf8mb4'
}

# ----------- 数据处理流程 -----------
try:
    logger.info("连接数据库...")
    conn = pymysql.connect(**db_config)
    query = """
        SELECT Tag, Value, Timestamp
        FROM dailydata_sdzx
        WHERE Tag IN ('1期累计冷量', '2期累计冷量')
        ORDER BY Timestamp;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    logger.info(f"读取 {len(df)} 条记录成功。")

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    pivot_df = df.pivot(
        index='Timestamp',
        columns='Tag',
        values='Value').reset_index()
    pivot_df.columns.name = None
    pivot_df.rename(columns={
        '1期累计冷量': '一期累计冷量',
        '2期累计冷量': '二期累计冷量'
    }, inplace=True)
    pivot_df[['一期累计冷量', '二期累计冷量']] = pivot_df[[
        '一期累计冷量', '二期累计冷量']].round(0).astype('Int64')

    output_file = f"冷量累计数据_取整_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    pivot_df.to_excel(output_file, index=False)
    logger.info(f"写入 Excel 成功：{output_file}")

except Exception as e:
    logger.exception(f"程序运行失败: {e}")



