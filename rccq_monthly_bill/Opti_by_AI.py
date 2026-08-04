#!/usr/bin/env python
# coding: utf-8

import os
import datetime
import sys
import logging
import logging.config
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Border, Side

# 设置路径和配置
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
config_path = os.path.join(BASE_DIR, "logging.conf")
logging.config.fileConfig(config_path)
logger = logging.getLogger('applog')

# 加载模板和报告路径
def load_template():
    tmplate_path = os.path.join(BASE_DIR, "RCCQ HW Metering Report_temp202307.xlsx")
    return load_workbook(tmplate_path)

# 设置日期
def set_date(ws, now):
    if now.month == 1:
        ws['F6'] = datetime.datetime(now.year-1, 12, 1).strftime('%b %Y')
        ws['B8'] = datetime.datetime(now.year-1, 12, 1).strftime('%d.%m.%y')
    else:
        ws['F6'] = datetime.datetime(now.year, now.month - 1, 1).strftime('%b %Y')
        ws['B8'] = datetime.datetime(now.year, now.month - 1, 1).strftime('%d.%m.%y')
    ws['B9'] = datetime.datetime(now.year, now.month, 1).strftime('%d.%m.%y')

# 写入数据到 Excel
def write_to_excel(ws, col, row_start, data):
    for i, value in enumerate(data):
        ws.cell(row=row_start + i, column=col, value=value)

# 获取文件路径
def get_file_path(pattern):
    files = os.listdir(BASE_DIR)
    for f in files:
        if pattern in f:
            return os.path.join(BASE_DIR, f)
    return None

# 计算最大、最小值
def compute_max_min(df, column):
    return df.groupby(pd.Grouper(key='datetime', axis=0, freq='D')).agg({column: ['max', 'min']})

# 计算日用量
def calculate_dayuse(df):
    data_0 = df[df["datetime"].dt.hour == 0]
    data_0_s = data_0[:-1].reset_index(drop=True)
    data_0_e = data_0[1:].reset_index(drop=True)
    return data_0_e - data_0_s

# 计算最大负荷
def calculate_max_demand(df, column):
    return df.groupby(pd.Grouper(key='datetime', axis=0, freq='D'))[column].max()

# 主流程
try:
    now = datetime.datetime.now()
    current_date = now.strftime('%Y%m')
    last_month = (now.replace(day=1) - datetime.timedelta(days=1)).strftime('%Y%m')

    # 获取文件路径
    file_path = get_file_path('HW RTU_Monthly Report_' + current_date)
    # file_path = get_file_path("C:\\Users\\funny\\PycharmProjects\\rccq_monthly_bill\\HW RTU_Monthly Report_20250201000906275.xlsx")
    if not file_path:
        raise FileNotFoundError(f"Report file for {current_date} not found.")

    # 读取数据
    df = pd.read_excel(file_path, sheet_name='Report', header=1, parse_dates=['datetime'])
    df = df.dropna()  # 删除 NaN

    # 计算数据
    dayuse = calculate_dayuse(df)
    df_max_daily_QI = compute_max_min(df, 'QI')

    # 加载 Excel 模板
    wb2 = load_template()
    ws_summary = wb2['Summary']

    # 设置日期
    set_date(ws_summary, now)

    # 写入日用量和最大负荷
    ws_list = ['HotelLZ PreHeat', 'SvcAptLZ PreHeat', 'HotelHZ HT', 'HotelLZ HT']
    QQ_list = ['H1_QQ_9350_BTU', 'H2_QQ_9350_BTU', 'H3_QQ_9350_BTU']
    for i, j in zip(ws_list, QQ_list):
        write_to_excel(wb2[i], 5, 21, dayuse[j])
        write_to_excel(wb2[i], 3, 21, df_max_daily_QI[j])

    # 保存 Excel 文件
    report_path = os.path.join(BASE_DIR, last_month + "_HW.xlsx")
    wb2.save(report_path)
    logger.info(f"Report saved to {report_path}")

except Exception as e:
    logger.exception(f"Error occurred: {e}")
