import pandas as pd
import pymysql
import os
import mysql.connector
from sqlalchemy import create_engine
from urllib.parse import quote


def create_database(conn, database_name):
    """创建数据库"""
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    conn.commit()


def create_table(conn, database_name, table_name, df):
    """创建数据表"""
    cursor = conn.cursor()
    conn.select_db(database_name)

    # 获取数据表字段名和类型
    cols = ', '.join([f"`{c}` {t}" for c, t in zip(df.columns, df.dtypes)])

    # 创建表
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})"
    cursor.execute(sql)
    conn.commit()


def insert_data(conn, database_name, table_name, df):
    """插入数据"""
    cursor = conn.cursor()
    conn.select_db(database_name)

    # 将DataFrame转为list of tuples
    data = df.to_records(index=False).tolist()

    # 构造插入SQL语句
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    print(sql)

    # 执行插入操作
    cursor.executemany(sql, data)
    conn.commit()


# 连接MySQL数据库
# conn = pymysql.connect(
#     host='183.66.202.50',
#     port=26360,
#     user='root',
#     password='1qazXSW@',
#     charset='utf8mb4',  # 确保字符集支持中文
#     cursorclass=pymysql.cursors.DictCursor
# )
# cursor = conn.cursor()
# 创建数据库和数据表
database_name = 'dailyoa_4_all'
table_name = 'dailyoa_4_all'
# create_database(conn, database_name)

# 获取文件夹路径并遍历文件
folder_path = r"C:\Users\funny\Desktop\RCCQ_OA"
file_list = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
df_list = []
for file in file_list:
    file_path = os.path.join(folder_path, file)
    df = pd.read_excel(file_path, sheet_name='Data')
    del df['end_time']
    df_list.append(df)

df_combine = pd.concat(df_list, ignore_index=True)
column_list = df_combine.columns.tolist()
df_combine.to_csv(r"C:\Users\funny\Desktop\test1.csv")
df_unpivot = pd.melt(df_combine,
                     id_vars='Record_time',
                     value_vars=column_list,
                     var_name='tag',
                     value_name='value')
df_unpivot['Record_time'] = pd.to_datetime(df_unpivot['Record_time'])
df_unpivot['tag'] = df_unpivot['tag'].apply(str)
df_unpivot['value'] = pd.to_numeric(df_unpivot['value'])
# print(df_unpivot.info())
# df_unpivot.to_csv(r"C:\Users\funny\Desktop\test.csv")
# create_table(conn, database_name, table_name, df_unpivot)  # 如果表不存在则创建
# insert_data(conn, database_name, table_name, df_unpivot)

# 关闭数据库连接
# cursor.close()
# conn.close()
# 建立数据库连接
# mydb = mysql.connector.connect(
host = '183.66.202.50',
port = 26360,
user = 'root',
password = '1qazXSW@',
database = "dailyoa_4_all"
# DATABASE_HOST = "10.10.10.110"
# DATABASE_NAME = "dbtest"
# DATABASE_USERNAME = "admin"
# DATABASE_PASSWORD = "admin@123"
# )
#
# # 将 DataFrame 写入 MySQL
# df_unpivot.to_sql('dailyoa_4_all', con=mydb, if_exists='replace', index=False)
# Create an SQLAlchemy engine
# engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

engine = create_engine(
    f'mysql+pymysql://root:%s@183.66.202.50:26360/dailyoa_4_all' %
    quote('1qazXSW@'))
# Write the DataFrame to the database
df_unpivot.to_sql(
    'dailyoa_4_all',
    con=engine,
    if_exists='replace',
    index=False)
print("Data has been written to MySQL database.")
