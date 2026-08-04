# 用于填写蜀都中心的月度账单

import pandas as pd
import pymysql
from openpyxl import load_workbook
import yaml
import logging
import logging.config
from datetime import datetime
import os
import sys

# ============ 目录与路径 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
LOGGING_PATH = os.path.join(BASE_DIR, "logging.yaml")
TEMPLATE_PATH = os.path.join(
    BASE_DIR,
    "template",
    "Shudu Metering Report template.xlsx")
OUTPUT_PATH = os.path.join(BASE_DIR, "Shudu Metering Report filled.xlsx")
START_ROW = 21
TIMES = ["00:00:00", "08:00:00", "18:00:00", "22:00:00"]
COLUMN_MAP = {
    "00:00:00": "B",
    "08:00:00": "C",
    "18:00:00": "D",
    "22:00:00": "E"
}

# ============ 初始化日志 ============
try:
    with open(LOGGING_PATH, "r", encoding="utf-8") as f:
        logging_config = yaml.safe_load(f)
        logging.config.dictConfig(logging_config)
except Exception as e:
    print("无法加载日志配置文件 logging.yaml")
    print(e)
    sys.exit(1)

logger = logging.getLogger(__name__)


def main():
    try:
        logger.info("读取配置文件...")
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        db_config = {
            "host": config["mysql"]["host"],
            "port": config["mysql"]["port"],
            "user": config["mysql"]["user"],
            "password": config["mysql"]["password"],
            "db": config["mysql"]["database"],
            "charset": "utf8mb4"
        }

        # 时间范围
        today = datetime.today()
        first_day_this_month = datetime(today.year, today.month, 1)
        last_month_end = first_day_this_month - pd.Timedelta(days=1)
        last_month_start = datetime(
            last_month_end.year, last_month_end.month, 1)
        start_str = last_month_start.strftime("%Y-%m-%d")
        end_str = (last_month_end + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

        logger.info(f"查询时间范围：{start_str} ~ {end_str}")

        query = f"""
            SELECT Timestamp, Tag, Value
            FROM dailydata_sdzx
            WHERE Tag IN ('1期累计冷量', '2期累计冷量')
            AND Timestamp >= '{start_str}' AND Timestamp < '{end_str}'
            AND TIME(Timestamp) IN ({','.join([f"'{t}'" for t in TIMES])})
        """

        logger.info("连接数据库并执行查询...")
        conn = pymysql.connect(**db_config)
        df = pd.read_sql(query, conn)
        conn.close()
        logger.info(f"成功读取 {len(df)} 条记录。")

        df["Date"] = df["Timestamp"].dt.date
        df["Time"] = df["Timestamp"].dt.strftime("%H:%M:%S")

        def extract_values(tag):
            sub = df[df["Tag"] == tag]
            result = {}
            for t in TIMES:
                values = sub[sub["Time"] == t].sort_values(
                    "Date")["Value"].round(0).astype("Int64").tolist()
                result[t] = values
            return result

        logger.info("整理数据...")
        data_1 = extract_values("1期累计冷量")
        data_2 = extract_values("2期累计冷量")

        logger.info("打开模板文件...")
        wb = load_workbook(TEMPLATE_PATH)
        sheets = {
            "1期累计冷量": wb["一期"],
            "2期累计冷量": wb["二期"]
        }

        logger.info("写入数据到模板...")
        for tag, dataset in [("1期累计冷量", data_1), ("2期累计冷量", data_2)]:
            sheet = sheets[tag]
            for t in TIMES:
                values = dataset[t]
                col = COLUMN_MAP[t]
                for i, val in enumerate(values):
                    sheet[f"{col}{START_ROW + i}"] = val

        wb.save(OUTPUT_PATH)
        logger.info(f"✅ 写入完成，文件保存为：{OUTPUT_PATH}")

    except Exception as e:
        logger.exception("❌ 程序运行失败")


if __name__ == "__main__":
    main()
