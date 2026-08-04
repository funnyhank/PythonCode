#用于导出数据库中蜀都中心上月的数据，具体的查询语句在query/cooling_data.sql中
#2025-8-7收到张的要求，导出的数据中要包含温度和流量等明细数据
#mysq的配置文件在config.yaml中，log的配置文件在logging.yaml中

import pandas as pd
import pymysql
import yaml
import logging
import logging.config
from datetime import datetime
import os

# ---------- 设置目录 ----------
# 获取脚本所在的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- 加载日志配置 ----------
try:
    with open(os.path.join(BASE_DIR, "logging.yaml"), "r", encoding="utf-8") as f:
        logging_config = yaml.safe_load(f)
        logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
except Exception as e:
    # 如果日志配置加载失败，则使用基本配置
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.error(f"加载日志配置失败: {e}")

# ---------- 加载数据库配置 ----------
try:
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
except Exception as e:
    logger.exception(f"加载数据库配置失败: {e}")
    exit() # 如果配置失败，程序退出

# ---------- 主程序 ----------
def main():
    """
    主函数，负责数据查询、处理和导出。
    """
    try:
        # ---------- 读取 SQL 文件 ----------
        sql_file_path = os.path.join(BASE_DIR, "query", "cooling_data.sql")
        logger.info(f"正在读取 SQL 文件: {sql_file_path}")
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_query = f.read()

        # ---------- 查询数据 ----------
        logger.info("开始连接数据库...")
        # 使用 with 语句自动管理连接，确保其被正确关闭
        with pymysql.connect(**db_config) as conn:
            df = pd.read_sql(sql_query, conn)
        logger.info(f"成功从数据库读取 {len(df)} 条记录。")

        # ---------- 数据处理 ----------
        # 将时间戳列转换为 datetime 类型
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # 数据透视：将长格式数据转换为宽格式
        pivot_df = df.pivot(
            index='Timestamp',
            columns='Tag',
            values='Value'
        ).reset_index()
        pivot_df.columns.name = None # 移除列名中的 'Tag'

        # 重命名列，使其更具可读性
        pivot_df.rename(columns={
            '1期累计冷量': '一期累计冷量',
            '2期累计冷量': '二期累计冷量',
            '1期供水温度': '一期供水温度',
            '1期回水温度': '一期回水温度',
            '1期流量': '一期流量',
            '2期供水温度': '二期供水温度',
            '2期回水温度': '二期回水温度',
            '2期流量': '二期流量'
        }, inplace=True)

        # 仅对指定的两列进行取整和类型转换
        for col in ['一期累计冷量', '二期累计冷量','一期流量','二期流量']:
            if col in pivot_df.columns:
                pivot_df[col] = pd.to_numeric(
                    pivot_df[col], errors='coerce'
                ).round(0).astype('Int64')
        for col in ['一期供水温度', '一期回水温度','二期供水温度','二期回水温度']:
            if col in pivot_df.columns:
                pivot_df[col] = pd.to_numeric(
                    pivot_df[col], errors='coerce'
                ).round(1)
        logger.info("数据处理完成，已对指定列取整。")

        # ---------- 写入 Excel ----------
        # 构造文件名，确保其在文件系统中是有效的
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"冷量累计数据_{timestamp_str}.xlsx"
        output_file_path = os.path.join(BASE_DIR, output_filename)

        pivot_df.to_excel(output_file_path, index=False)
        logger.info(f"数据已成功写入 Excel 文件: {output_file_path}")

    except Exception as e:
        logger.exception("程序运行失败，请检查错误日志。")

if __name__ == "__main__":
    main()