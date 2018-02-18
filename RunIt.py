# -*- coding: utf-8 -*-
# from threading import Thread
# from Crawler import Crawler
import requests


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
resp = requests.get("http://google.com")
print resp.content
