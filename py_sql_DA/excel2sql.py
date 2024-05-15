import pymysql

# 打开数据库连接
try:
    db = pymysql.connect(
        host='localhost',
        user='root',
        passwd='Abb1234#',
        port=3306)
    print('连接成功！')
except BaseException:
    print('something wrong!')

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 使用 execute()  方法执行 SQL 查询
cursor.execute("SELECT VERSION()")

# 使用 fetchone() 方法获取单条数据.
data = cursor.fetchone()

print("Database version : %s " % data)

# 关闭数据库连接
db.close()

'''
连接成功！
Database version : 8.0.25
'''
