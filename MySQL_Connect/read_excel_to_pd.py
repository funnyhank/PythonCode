import pandas as pd
import pymysql
import sqlalchemy
import openpyxl
import os
from sqlalchemy import create_engine
pd.options.display.max_seq_items = None

folder_path = r"C:\Users\funny\Desktop\RCCQ_OA"
file_list = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

for file in file_list:
    file_path = os.path.join(folder_path, file)
    df = pd.read_excel(file_path, sheet_name='Data')
    column_list = df.columns.tolist()
# print(df.head())
df_unpivot = pd.melt(df,
                     id_vars='Record_time',
                     value_vars=column_list,
                     var_name='tag',
                     value_name='value')
print(df_unpivot.tail())
