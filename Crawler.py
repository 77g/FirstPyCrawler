# -*- coding: utf-8 -*-
from API.Fetch import SogouAPI
from Queue import Queue
from threading import Thread



class CrawlerThread(Thread):
    def __init__(self, queue):
        self.queue = queue
        self.sogou_api = SogouAPI()
        Thread.__init__(self)

    def run(self):
        n = 2
        # 1. info = queue.get => what is in the queue?
        # 2. m.update(info['url']) seems a kv pair, this is an URL
        while n > 0:
            print "run %d time" % n
            n -= 1


class Crawler:
    def __init__(self, thread_num):
        self.queue = Queue()
        self.thread_pools = []
        self.sogou_api = SogouAPI()

        for i in range(thread_num):
            self.thread_pools.append(CrawlerThread(self.queue))

        for crawler_thread in self.thread_pools:
            crawler_thread.start()

    def start(self):
        pass

