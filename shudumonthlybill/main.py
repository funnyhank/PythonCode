
# 2023年9月12日，新要求，一期工作日8：00到18：00无加班供应，周末8点到18点，全算加班供应
# 二期工作日8：00到18：00正常供应，18：00到22点加班，周末8点到18点，全算加班供应
# 考虑一期二期分开处理


import pandas as pd
from openpyxl import load_workbook
from chinese_calendar import is_workday
from datetime import datetime
import sys
import os

pd.options.mode.chained_assignment = None


def write_dayuse_to_excel(shtname, dfname):
    alist = dfname
    ws = wb2[shtname]
    # cell_range = ws['E21':'E51']
    i = 1
    while i < len(alist) + 1:
        ws.cell(row=i + 20, column=3, value=alist[i])
        i += 1


def write_day_OT_to_excel(shtname, dfname):
    alist = dfname
    ws = wb2[shtname]
    # cell_range = ws['C21':'C51']
    i = 1
    while i < len(alist) + 1:
        ws.cell(row=i + 20, column=5, value=alist[i])
        i += 1


def write_date(shtname):
    ws = wb2[shtname]
    ws['D6'] = last_month


def write_start_value(shtname, startvalue):
    ws = wb2[shtname]
    ws['E8'] = startvalue
    # ws['E8'] = endvalue


def write_end_value(shtname, endvalue):
    ws = wb2[shtname]
    ws['E9'] = endvalue


def write_start_date(shtname):
    ws = wb2[shtname]
    ws['B8'] = datetime(now.year, now.month - 1, 1).strftime('%d.%m.%y')


def write_end_date(shtname):
    ws = wb2[shtname]
    ws['B9'] = datetime(now.year, now.month, 1).strftime('%d.%m.%y')


BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
tmplate_path = os.path.join(BASE_DIR, "Shudu Metering Report temp.xlsx")
report_path = os.path.join(BASE_DIR, 'sudu08.xlsx')
print(report_path)
df = pd.read_excel('report_path')
df.head()

col_list = ['入口温度', '出口温度', '累计冷量', '累计热量', '累计流量', '瞬时流量',
            '入口温度_1', '出口温度_2', '累计冷量_3', '累计热量_4', '累计流量_5', '瞬时流量_6'
            ]
for i in col_list:
    df[i] = pd.to_numeric(df[i], errors='coerce').fillna(0)

df.drop(columns=['入口温度', '出口温度', '累计热量', '累计流量', '瞬时流量',
                 '入口温度_1', '出口温度_2', '累计热量_4', '累计流量_5', '瞬时流量_6'
                 ], axis=1, inplace=True)


df1 = df.drop(columns='累计冷量_3')
df2 = df.drop(columns='累计冷量')


df1_8 = df1[(df1['时间'].dt.minute == 0) & (df['时间'].dt.hour == 8)]
df1_18 = df1[(df1['时间'].dt.minute == 0) & (df['时间'].dt.hour == 18)]


df1_8.reset_index(inplace=True, drop=True)
df1_8.index = df1_8.index + 1
df1_18.reset_index(inplace=True, drop=True)
df1_18.index = df1_18.index + 1

df1_normal_day = df1_18 - df1_8

df1_normal_day['时间'] = df1_8['时间']


df1_normal_day['时间'] = df1_normal_day['时间'].apply(
    lambda x: datetime.strftime(x, '%Y/%m/%d'))


df1_normal_day['day_of_week'] = df1_8['时间'].apply(
    lambda x: datetime.strftime(x, '%A'))  # 添加星期列
df1_normal_day['OT'] = df1_normal_day['累计冷量']
df1_normal_day['workday'] = df1_8['时间'].apply(
    lambda x: 1 if is_workday(x) else 0)
df1_normal_day['weekend'] = df1_8['时间'].apply(
    lambda x: 0 if is_workday(x) else 1)


df1_normal_day['累计冷量'] = df1_normal_day['累计冷量'] * df1_normal_day['workday']
df1_normal_day['OT'] = df1_normal_day['OT'] * df1_normal_day['weekend']
df1_to_excel = df1_normal_day.drop(
    columns=['day_of_week', 'weekend', 'workday'])


df2_8 = df2[(df2['时间'].dt.minute == 0) & (df2['时间'].dt.hour == 8)]
df2_18 = df2[(df2['时间'].dt.minute == 0) & (df2['时间'].dt.hour == 18)]
df2_22 = df2[(df2['时间'].dt.minute == 0) & (df2['时间'].dt.hour == 22)]
df2_8.reset_index(inplace=True, drop=True)
df2_8.index = df2_8.index + 1
df2_18.reset_index(inplace=True, drop=True)
df2_18.index = df2_18.index + 1
df2_22.reset_index(inplace=True, drop=True)
df2_22.index = df2_22.index + 1
df2_daily_OT = df2_22 - df2_18
df2_daily_OT['时间'] = df1_normal_day['时间']
df2_normal_day = df2_18 - df2_8
df2_normal_day['时间'] = df1_normal_day['时间']


df2_normal_day['OT'] = df2_normal_day['累计冷量_3']
df2_normal_day['workday'] = df1_8['时间'].apply(
    lambda x: 1 if is_workday(x) else 0)
df2_normal_day['weekend'] = df1_8['时间'].apply(
    lambda x: 0 if is_workday(x) else 1)
df2_normal_day['累计冷量'] = df2_normal_day['累计冷量_3'] * df2_normal_day['workday']
df2_normal_day['OT'] = df2_normal_day['OT'] * df2_normal_day['weekend']
df2_daily_OT['workday'] = df1_8['时间'].apply(
    lambda x: 1 if is_workday(x) else 0)
df2_daily_OT['累计冷量_3'] = df2_daily_OT['累计冷量_3'] * df2_daily_OT['workday']
df2_to_excel = df2_normal_day.drop(columns=['累计冷量_3', 'weekend', 'workday'])
df2_to_excel['OT'] = df2_to_excel['OT'] + df2_daily_OT['累计冷量_3']
df2_to_excel.insert(1, '累计冷量', df2_to_excel.pop('累计冷量'))  # 交换列位置
# df2_to_excel['累计冷量2'] = df2_to_excel['累计冷量']


df_to_excel = pd.concat([df1_to_excel, df2_to_excel], axis=1)
df_excel = df_to_excel.drop(columns=['时间', '时间'])
df_excel.columns = ['累计冷量_1', 'OT_1', '累计冷量_2', 'OT_2']
df_use_excel = df_excel.iloc[:, [0, 2]]
df_OT_excel = df_excel.iloc[:, [1, 3]]

wb2 = load_workbook("tmplate_path")

ws_list = ['一期', '二期']
QQ_list = ['累计冷量_1', '累计冷量_2']
OT_list = ['OT_1', 'OT_2']


current_date = datetime.now().strftime('%Y%m')  # 获取当前年月格式2023xx
now = datetime.now()
last_month = datetime(now.year, now.month - 1, 1).strftime('%Y%m')


for i, j in zip(ws_list, QQ_list):
    write_dayuse_to_excel(i, df_use_excel[j])
for m, n in zip(ws_list, OT_list):
    write_day_OT_to_excel(m, df_OT_excel[n])
write_date('Summary')
write_end_date('一期')
write_start_date('一期')
write_start_value('一期', df['累计冷量'].min())
write_start_value('二期', df['累计冷量_3'].min())
write_end_value('一期', df['累计冷量'].max())
write_end_value('二期', df['累计冷量_3'].max())
wb2.save("Shudu Metering Report" + last_month + ".xlsx")
