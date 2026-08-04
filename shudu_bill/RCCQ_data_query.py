# -*- coding: utf-8 -*-

# 用于导出数据库中蜀都中心上月的数据，具体的查询语句在query/cooling_data.sql中
# 2025-12-11收到张的要求，导出的数据中要包含温度和流量等明细数据
# mysq的配置文件在config.yaml中，log的配置文件在logging.yaml中

import pandas as pd
import yaml
import logging
import logging.config
from datetime import datetime
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus  # 导入 urllib.parse 模块

# ---------- 设置目录 ----------
# 获取脚本所在的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- 加载日志配置 ----------
try:
    # 确保日志文件夹存在
    logs_dir = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    with open(os.path.join(BASE_DIR, "logging.yaml"), "r", encoding="utf-8") as f:
        logging_config = yaml.safe_load(f)
        logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
except Exception as e:
    # 如果日志配置加载失败，则使用基本配置
    logging.basicConfig(
        level=logging.INFO,
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
    }
except Exception as e:
    logger.exception(f"加载数据库配置失败: {e}")
    exit()  # 如果配置失败，程序退出


# ---------- 主程序 ----------
def main():
    """
    主函数，负责数据查询、处理和导出。
    """
    try:
        # ---------- 读取 SQL 文件 ----------
        sql_file_path = os.path.join(BASE_DIR, "query", "rccq_data_query.sql")
        logger.info(f"正在读取 SQL 文件: {sql_file_path}")
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_query = f.read()

        # ---------- 查询数据 (使用 SQLAlchemy) ----------
        logger.info("开始连接数据库...")
        # 对密码进行 URL 编码以处理特殊字符，特别是 @ 符号
        encoded_password = quote_plus(db_config['password'])

        # 构建 SQLAlchemy 连接 URI
        db_uri = f"mysql+pymysql://{db_config['user']}:{encoded_password}@{
            db_config['host']}:{db_config['port']}/{db_config['db']}"

        # 创建 SQLAlchemy 引擎
        engine = create_engine(db_uri)

        # 使用 with 语句自动管理连接
        with engine.connect() as conn:
            # 修改这里: 手动替换 % 为 %% 以避免 Python 格式化错误
            # This is the key change to handle the %Y issue.
            # We explicitly tell pandas that the query has no parameters,
            # which forces pymysql to treat the '%' as a literal.
            sql_query_escaped = sql_query.replace('%', '%%')
            df = pd.read_sql(sql_query_escaped, conn)
        logger.info(f"成功从数据库读取 {len(df)} 条记录。")

        # ---------- 数据处理 ----------
        # 将时间戳列转换为 datetime 类型
        df['Record_time'] = pd.to_datetime(df['Record_time'])

        # 数据透视：将长格式数据转换为宽格式
        pivot_df = df.pivot(
            index='Record_time',
            columns='Tag',
            values='Value'
        ).reset_index()
        pivot_df.columns.name = None  # 移除列名中的 'Tag'

        # 定义列名映射和处理方式
        column_map = {
            'east11A': 'east11A',
            'east11B': 'east11B',
            'west21A': 'west21A',
            'west21B': 'west21B',
            'D1_QQ_1150_BTU': 'D1_QQ_1150_BTU',
            'D2_QQ_1150_BTU': 'D2_QQ_1150_BTU',
            'D3_QQ_1150_BTU': 'D3_QQ_1150_BTU',
            'D4_QQ_1150_BTU': 'D4_QQ_1150_BTU',
            'D5_QQ_1150_BTU': 'D5_QQ_1150_BTU',
            'D6_QQ_1150_BTU': 'D6_QQ_1150_BTU',
            'D7_QQ_1150_BTU': 'D7_QQ_1150_BTU',
            'D8_QQ_1150_BTU': 'D8_QQ_1150_BTU',
            'QI_120A': 'QI_120A',
            'QI_120B': 'QI_120B',
            'QI_120D': 'QI_120D',
            'QI_120E': 'QI_120E',
            'QI_120F': 'QI_120F',
            'QI_120H': 'QI_120H',
            'QI_120K': 'QI_120K',
            'QI_120M': 'QI_120M'
        }

        # 重命名列
        pivot_df.rename(columns=column_map, inplace=True)

        # # 定义需要处理的列及其处理方式，更加简洁
        # integer_cols = ['一期累计冷量', '二期累计冷量', '一期流量', '二期流量']
        # float_cols = ['一期供水温度', '一期回水温度', '二期供水温度', '二期回水温度']
        #
        # # 对整数列进行处理
        # for col in [c for c in integer_cols if c in pivot_df.columns]:
        #     pivot_df[col] = pd.to_numeric(
        #         pivot_df[col], errors='coerce').round(0).astype('Int64')
        #
        # # 对浮点数列进行处理
        # for col in [c for c in float_cols if c in pivot_df.columns]:
        #     pivot_df[col] = pd.to_numeric(
        #         pivot_df[col], errors='coerce').round(1)
        #
        # logger.info("数据处理完成，已对指定列取整。")

        # ---------- 写入 Excel ----------
        # 构造文件名，确保其在文件系统中是有效的
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"RCCQ查询数据_{timestamp_str}.xlsx"
        output_file_path = os.path.join(BASE_DIR, output_filename)

        pivot_df.to_excel(output_file_path, index=False)
        logger.info(f"数据已成功写入 Excel 文件: {output_file_path}")

    except Exception:
        logger.exception("程序运行失败，请检查错误日志。")


if __name__ == "__main__":
    main()
