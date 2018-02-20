# -*- coding: utf-8 -*-
# from threading import Thread
# from Crawler import Crawler
import requests
import re
import json


# class Sample(Thread):
#    def __init__(self):
#        super(Sample, self).__init__()
#        Thread.__init__(self)

#    def run(self):
#        print "This is running"


# sa = Sample()
# print sa.start()

# cl = Crawler(10)
# cl.start()
resp = requests.get("http://mp.weixin.qq.com/profile?src=3&timestamp=1519013909&ver=1&signature=0MRsaIdeeICQ9Zrlf95P6J5*6W6xgv0zPcm*D831zrOz-T-48Ms024vTEpVTIBbZ0bCMXSOeKafBaJF7-or77A==")
print resp.status_code

article_re = re.compile('var msgList = (.*?)}}]};')

articles = article_re.findall(resp.text)
articles = articles[0] + '}}]}'  # what?? 一定要搞清楚这个结构。。。
articles = json.loads(articles)

for article in articles['list']:
    if str(article['comm_msg_info'].get('type', '')) != '49':
        continue
    print article['comm_msg_info'].get('datetime', '')






# lis = {list:[{"app":{a}}]}
