import matplotlib.pyplot as plt
import pymysql

# 连接数据库
db = pymysql.connect(host='localhost', user='root',
                     passwd='Abb1234#', port=3306, db='test_db')

# 开启一个游标cursor
cursor = db.cursor()

# 获取表(monthlyreport_4)里的数据(QI_120A),使用sql语句
sql = 'select "QI_120A" from monthlyreport_4'

# 执行sql中的语句
cursor.execute(sql)

# 将获取到的sql数据全部显示出来
result = cursor.fetchall()

# 定义需要用上的空数据数组，然后通过遍历数据库的数据将数据附上去
xname = []
ynum = []

# 遍历表里的数据
for x in result:
    xname.append(x[0])
    ynum.append(x[0])

# 创建一个figure（一个窗口）来显示条形图
plt.figure()
plt.bar(xname, ynum)
plt.xlabel('time')
plt.ylabel('QI')
for x, y in enumerate(ynum):
    plt.text(x, y, '%s' % y)

# 创建一个figure（一个窗口）来显示折线图
plt.figure()
plt.plot(xname, ynum)
for x, y in enumerate(ynum):
    plt.text(x, y, '%s' % y)

# 显示图表
plt.show()

# 关闭游标和数据库
cursor.close()
db.close()
