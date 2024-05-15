#!/usr/bin/env python
# coding: utf-8

import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
import datetime
from openpyxl import load_workbook
from openpyxl.styles.borders import Border, Side
import sys
import logging.config
import xlwings as xw
app = xw.App(visible=True, add_book=False)
app.display_alerts = False    # 关闭一些提示信息，可以加快运行速度。 默认为 True。
app.screen_updating = True   # 更新显示工作表的内容。默认为 True。关闭它也可以提升运行速度。
pd.options.mode.chained_assignment = None


def write_dayuse_to_excel(shtname, dfname):
    alist = dfname
    ws = wb2[shtname]
    # cell_range = ws['E21':'E51']
    i = 0
    while i < len(alist):
        ws.cell(row=i + 21, column=5, value=alist[i])
        i += 1


def write_day_max_demand(shtname, dfname):
    alist = dfname
    ws = wb2[shtname]
    # cell_range = ws['C21':'C51']
    i = 0
    while i < len(alist):
        ws.cell(row=i + 21, column=3, value=alist[i])
        i += 1


def write_date(shtname):
    ws = wb2[shtname]
    if now.month == 1:
        ws['D6'] = datetime.datetime(now.year - 1, 12, 1).strftime('%b %Y')
    else:
        ws['D6'] = datetime.datetime(
            now.year, now.month - 1, 1).strftime('%b %Y')
    # ws['D6'] = datetime.datetime(now.year, now.month - 1, 1).strftime('%b %Y')


def write_start_value(shtname, startvalue):
    ws = wb2[shtname]
    ws['E8'] = startvalue
    # ws['E8'] = endvalue


def write_end_value(shtname, endvalue):
    ws = wb2[shtname]
    ws['E9'] = endvalue


def write_start_date(shtname):
    ws = wb2[shtname]
    if now.month == 1:
        ws['B8'] = datetime.datetime(
            now.year - 1,
            12,
            1).strftime('%d.%m.%y')
    else:
        ws['B8'] = datetime.datetime(
            now.year,
            now.month - 1,
            1).strftime('%d.%m.%y')


def write_end_date(shtname):
    ws = wb2[shtname]
    ws['B9'] = datetime.datetime(now.year, now.month, 1).strftime('%d.%m.%y')


# def main():
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
config_path = os.path.join(
    BASE_DIR, "logging.conf")
logging.config.fileConfig(config_path)
logger = logging.getLogger('applog')

try:
    current_date = datetime.datetime.now().strftime('%Y%m')  # 获取当前年月格式2023xx
    now = datetime.datetime.now()
    if now.month == 1:
        last_month = datetime.datetime(now.year - 1, 12, 1).strftime('%Y%m')
    else:
        last_month = datetime.datetime(
            now.year, now.month - 1, 1).strftime('%Y%m')
    # last_month = datetime.datetime(now.year, now.month - 1, 1).strftime('%Y%m')
    # monthfirstday = datetime.datetime.now().strftime('%Y%m%d')
    # monthfirstday
    today = datetime.datetime.today()
    # monthfirstday = datetime.datetime(today.year, today.month, 1, 0, 0, 0).strftime('%Y%m%d %H:%M:%S')

    tmplate_path = os.path.join(
        BASE_DIR, "202309_CHW_temp.xlsx")
    report_path = os.path.join(BASE_DIR, last_month)
    # path1 = r"C:\Users\hank\PythonCode\Monthlybill"
    # currentPath = os.getcwd().replace('\\', '/')    # 获取当前路径
    # print(currentPath)
    # print(BASE_DIR)
    files = os.listdir(BASE_DIR)
    pattern = 'CHW RTU_Monthly Report_' + current_date
    for f in files:
        if pattern in f:
            path = f
    # print(path)
    # 模糊查找，文件夹下含有'CHW RTU_Monthly Report_'+current_date的文件
    filepath = BASE_DIR + "\\" + path
    # print(filepath)
    # 需要读取上一月的数据
    pattern_lastMonth = 'CHW RTU_Monthly Report_' + last_month
    for f in files:
        if pattern_lastMonth in f:
            path_last_month = f
    filepath_lastmonth = BASE_DIR + "\\" + path_last_month

    df = pd.read_excel(filepath,
                       sheet_name='Report',
                       header=1,
                       parse_dates=['datetime']
                       )
    logger.info("CHW monthly report Successfully imported!")
    df = df.dropna()  # 删除NaN
    df_lastmonth = pd.read_excel(filepath_lastmonth,
                                 sheet_name='Report',
                                 header=1,
                                 parse_dates=['datetime']
                                 )
    df_lastmonth = df_lastmonth.dropna()  # 删除NaN

    df = pd.concat([df_lastmonth.tail(1), df[1:]])  # 用上月最后一行替换当月第一行
    df.reset_index(drop=True, inplace=True)

    # 获取每日最大负荷QI
    df_max_daily_QI = df.groupby(pd.Grouper(key='datetime', axis=0,
                                            freq='D')).max()  # 用于每天的最大负荷需求
    df_max_daily_QI.drop(df_max_daily_QI.tail(1).index, inplace=True)  # 删除最后一行

    df.drop(df.columns[9:105], axis=1, inplace=True)  # 删除后面的列
    # df.drop(df.index[0], inplace=True)  # 删除第一行
    daymin = df.groupby(pd.Grouper(key='datetime', axis=0,
                                   freq='D')).min()
    daymin_s = daymin[:-1]
    daymin_e = daymin[1:]

    data_0 = df[df["datetime"].dt.hour == 0]  # .dt获取每天某小时的数据
    data_0_s = data_0[:-1]
    data_0_e = data_0[1:]
    data_0_e.reset_index(inplace=True, drop=True)
    data_0_e.index = data_0_e.index + 1
    data_0_s.reset_index(
        inplace=True, drop=True
    )  # 为了方便用pandas的减法，需要将index重置，这里用到reset_index
    # data_0_e=data_0_e.drop(columns=[Index])
    # data_0_s=data_0_s.drop(columns=[Index])
    data_0_s.index = data_0_s.index + 1
    dayuse = (
        data_0_e
        - data_0_s
    )
    # dayuse.drop(dayuse['datetime'],axis=1,inplace=True)
    # dayuse.index = daymin_s.index

    dayuse.reset_index(drop=True, inplace=True)
    dayuse.drop(columns=['datetime'], axis=1, inplace=True)
    dayuse.set_index(daymin_s.index, inplace=True, verify_integrity=True)

    wb2 = load_workbook(tmplate_path)
    # sheet_name = wb2.sheetnames
    # print(sheet_name)

    write_date('Summary')
    write_end_date('PodiumE')
    write_start_date('PodiumE')

    ws_list = ['PodiumE', 'PodiumW', 'HotelHZ',
               'HotelLZ', 'OfficeHZ', 'OfficeLZ', 'SvcAptHZ', 'SvcAptLZ']
    QI_list = ['D1_QI_1150_BTU', 'D2_QI_1150_BTU', 'D3_QI_1150_BTU',
               'D4_QI_1150_BTU', 'D5_QI_1150_BTU', 'D6_QI_1150_BTU',
               'D7_QI_1150_1_BTU', 'D8_QI_1150_2_BTU']
    QQ_list = [
        'D1_QQ_1150_BTU',
        'D2_QQ_1150_BTU',
        'D3_QQ_1150_BTU',
        'D4_QQ_1150_BTU',
        'D5_QQ_1150_BTU',
        'D6_QQ_1150_BTU',
        'D7_QQ_1150_BTU',
        'D8_QQ_1150_BTU']
    for i, j in zip(ws_list, QQ_list):
        write_start_value(i, df_lastmonth[j].max())
        write_end_value(i, df[j].max())
        write_dayuse_to_excel(i, dayuse[j])
    for m, n in zip(ws_list, QI_list):
        write_day_max_demand(m, df_max_daily_QI[n])
    logger.info("Successfully writed chiller water bill to excel")

    wb2.save(report_path + "_CHW.xlsx")
    wb = app.books.open(report_path + "_CHW.xlsx")
    sheet_counts = wb.sheets.count
    i = 1
    while i < sheet_counts:
        sht = wb.sheets[i]
        for row in sht.range('F21:F51'):
            row.api.Borders(10).LineStyle = 1
            row.api.Borders(10).Weight = 2
        for row in sht.range('F13:F16'):
            row.api.Borders(10).LineStyle = 1
            row.api.Borders(10).Weight = 2
        for row in sht.range('F18:F19'):
            row.api.Borders(10).LineStyle = 1
            row.api.Borders(10).Weight = 2
        i += 1
    summary_sheet = wb.sheets['Summary']
    for row in summary_sheet.range('D8:D11'):
        row.api.Borders(10).LineStyle = 1
        row.api.Borders(10).Weight = 2
    for row in summary_sheet.range('D13:D14'):
        row.api.Borders(10).LineStyle = 1
        row.api.Borders(10).Weight = 2
    for row in summary_sheet.range('D16:D46'):
        row.api.Borders(10).LineStyle = 1
        row.api.Borders(10).Weight = 2
    wb.save()
    wb.close()
except Exception as e:
    logger.exception(e)
#
# if __name__ == main:
#     main()
