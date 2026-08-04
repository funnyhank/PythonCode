import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.types import CHAR, INT

user = "root"
password = "Abb1234#"
host = "127.0.0.1"
db = "test_db"
# connetinfo = mysql+mysqlconnector://<'root'>:<'Abb1234#'>@<'localhost'>[:<3306>]/<'test_db'>
# engine = create_engine(connect_info) #use sqlalchemy to build link-engine
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:3306/{db}?charset=utf8',
                       echo=True, pool_recycle=7200, pool_size=5, max_overflow=10, pool_timeout=30)


coninfo = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='Abb1234#',
    db='test_db')
sql = "select * from monthlyreport_4"

df = pd.read_sql(sql=sql, con=coninfo)
print(df.head())
