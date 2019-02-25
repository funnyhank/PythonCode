import requests
from bs4 import BeautifulSoup

response = requests.get('https://bbs.huaweicloud.com/blogs/2f31bf73ec9f11e8bd5a7ca23e93a891')
#response.encoding = 'gbk'
result = response.text
soup = BeautifulSoup(result,'lxml')
print(soup.title)
print(soup.title.string)
print(soup.head)
print(soup.p)
