import pandas as pd
import os
import sys
from sqlalchemy import create_engine
from urllib.parse import quote
import yaml
import logging.config
import datetime
import re


with open('config.yaml', 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
config_path = os.path.join(
    BASE_DIR, "logging.conf")
logging.config.fileConfig(config_path)
logger = logging.getLogger('applog')
today = datetime.datetime.now().strftime('%Y%m%d')
# mydb = mysql.connector.connect(
#   host='localhost',
#   user="your_user",
#   password="Abb1234#",
#   database="rccqmonthlydata"
# )
engine = create_engine(
    f'mysql+pymysql://root:%s@localhost:3306/rccqmonthlydata' %
    quote('Abb1234#'))


def find_today_excel(folder_path):
    """
    在指定文件夹中查找以当天日期开头，.xlsx结尾的Excel文件

    Args:
      folder_path: 要搜索的文件夹路径

    Returns:
      匹配文件的路径，如果未找到则返回None
    """

    # 获取今天的日期，格式为YYYYMMDD
    today = datetime.date.today().strftime('%Y%m%d')
    prefix = "SHIRUI_DailyData_Template_"

    # 定义正则表达式模式
    pattern = rf"^{prefix}{today}.*\.xlsx$"

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if re.match(pattern, file):
                return os.path.join(root, file)
    return None


def write_month_report_data():
    # database_name = config['database_name']
    # table_name = config['table_name']

    excelpath = config['excelpath']
    sheetsname = config['sheetsname']

    folder_path = excelpath
    file_list = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    all_dfs = []
    for file in file_list:
        file_path = os.path.join(folder_path, file)
        df_excel = pd.read_excel(file_path, sheet_name=sheetsname, header=1)
        df_excel.drop(index=0, inplace=True)  # 删除第一行
        df_excel.drop([len(df_excel)], inplace=True)  # 删除最后一行
        df_excel.drop(labels='Tag', axis=1, inplace=True)
        all_dfs.append(df_excel)
    combined_df = pd.concat(all_dfs, ignore_index=True)
    excel_column_list = combined_df.columns.tolist()
    # print(df.head())
    df_unpivot = pd.melt(combined_df,
                         id_vars='time',
                         value_vars=excel_column_list,
                         var_name='tag',
                         value_name='value')
    df_unpivot['time'] = pd.to_datetime(df_unpivot['time'])
    df_unpivot['tag'] = df_unpivot['tag'].apply(str)
    df_unpivot['value'] = pd.to_numeric(df_unpivot['value'])

    # host = 'localhost',
    # port = 3306,
    # user = 'root',
    # password = 'Abb1234#',
    # database = "rccqmonthlydata"

    # engine = create_engine(
    #     f'mysql+pymysql://root:%s@localhost:3306/rccqmonthlydata' %
    #     quote('Abb1234#'))
    # Write the DataFrame to the database
    df_unpivot.to_sql(
        'monthlydata_rccq',
        con=engine,
        if_exists='replace',
        index=False)
    logger.info("Data has been written to MySQL database.")


def write_exist_oa_data():
    folder_path = config['excelpath']
    sheetsname = config['sheetsname']
    file_list = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
    all_dfs = []
    for file in file_list:
        file_path = os.path.join(folder_path, file)
        df_excel = pd.read_excel(file_path, sheet_name=sheetsname, header=0)
        # df_excel.drop(index=0, inplace=True)  # 删除第一行
        # df_excel.drop([len(df_excel)], inplace=True)  # 删除最后一行
        df_excel.drop(labels='end_time', axis=1, inplace=True)
        all_dfs.append(df_excel)
    combined_df = pd.concat(all_dfs, ignore_index=True)
    excel_column_list = combined_df.columns.tolist()

    df_unpivot = pd.melt(combined_df,
                         id_vars='Record_time',
                         value_vars=excel_column_list,
                         var_name='tag',
                         value_name='value')
    df_unpivot['Record_time'] = pd.to_datetime(df_unpivot['Record_time'])
    df_unpivot['tag'] = df_unpivot['tag'].apply(str)
    df_unpivot['value'] = pd.to_numeric(df_unpivot['value'])
    # engine = create_engine(
    #     f'mysql+pymysql://root:%s@localhost:3306/rccqmonthlydata' %
    #     quote('Abb1234#'))
    # Write the DataFrame to the database
    df_unpivot.to_sql(
        'dailydata_rccq',
        con=engine,
        if_exists='replace',
        index=False)
    logger.info("Old OA Data has been written to MySQL database.")


def write_current_oa_data():
    folder_path = config['excelpath']
    sheetsname = config['sheetsname']
    file_path = find_today_excel(folder_path=folder_path)
    # 读取Excel文件
    df_excel = pd.read_excel(
        file_path, sheet_name=sheetsname, header=0)
    df_excel.drop(labels='end_time', axis=1, inplace=True)
    excel_column_list = df_excel.columns.tolist()
    df_unpivot = pd.melt(df_excel,
                         id_vars='Record_time',
                         value_vars=excel_column_list,
                         var_name='tag',
                         value_name='value')
    df_unpivot['Record_time'] = pd.to_datetime(
        df_unpivot['Record_time'])
    df_unpivot['tag'] = df_unpivot['tag'].apply(str)
    df_unpivot['value'] = pd.to_numeric(df_unpivot['value'])
    df_unpivot.to_sql(
        'dailydata_rccq',
        con=engine,
        if_exists='append',
        index=False)
    logger.info("Today's OA Data has been add to MySQL database.")


if __name__ == '__main__':
    try:
        write_current_oa_data()
    except Exception as e:
        logger.error(e)
