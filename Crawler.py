# -*- coding: utf-8 -*-
from API.Fetch import SogouAPI
from Queue import Queue
from threading import Thread

import json
import hashlib


class CrawlerThread(Thread):
    def __init__(self, queue):
        self.queue = queue
        self.sogou_api = SogouAPI()
        Thread.__init__(self)

    def run(self):
        # 1. info = queue.get => what is in the queue?
        # 2. m.update(info['url']) seems a kv pair, this is an URL
        while True:
            info = self.queue.get()
            m = hashlib.md5()  # what is this?
            m.update(info['url'])
            unique_name = m.hexdigest()  # what is this?
            if 'profile' in info['url']:
                arts = self.sogou_api.fetch_history_urls_from_profile(info['url'])
                f = open(u'Content/%s' % unique_name, 'a')
                f.write(json.dump(arts).encode('utf-8'))
                f.close()

                for art in arts:
                    self.queue.put({'url': art['content_url'], 'title': art['title']})
            else:
                art = self.sogou_api.fetch(info['url'])
                f = open(u'Content/%s.html' % unique_name, 'w')
                f.write(art.encode('utf-8'))
                f.close()
            self.queue.task_done()


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
        print 'Start to processing...'
        gzh_info = self.sogou_api.fetch_gzh_info(keyword='九章算法')
        for info in gzh_info:
            self.queue.put({'url': info['profile_url'], 'title': info['wechat_id']})

        self.queue.join()
        print 'Finish'
