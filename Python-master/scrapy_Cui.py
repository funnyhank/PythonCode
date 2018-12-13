import requests
from pyquery import PyQuery as pq


url = 'https://www.zhihu.com/explore'
header = {
    'user-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"
}
html = requests.get(url, headers=header).text
doc = pq(html)
items = doc('.explore-tab .feed-item').items()
for item in items:
    question = item.find('h2').text()
    author = item.find('.author-link-line').text()
    answer = pq(item.find('.content').html()).text()
    file = open('explore.txt', 'a', encoding='utf-8')
    file.write('\n'.join([question,author,answer]))
    file.write('\n'+'='*50+'\n')
    file.close()
