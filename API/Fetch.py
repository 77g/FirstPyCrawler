# -*- coding: utf-8 -*-
from Constants import (
    SearchArticleTime,
    SearchArticleType
)
from Request import SogouRequest
from Utils.Parser import Parser
from Utils.SogouException import SogouCrawlerRequestsException
from PIL import Image

import json
import requests
import tempfile
import time


cache = {}  # dict()


class SogouAPI:

    def __init__(self, retries=5):
        self.retries = retries

    def fetch(self, url):
        resp = self.__get_and_unlock(
            url,
            unlock_function=self.__unlock_wechat,
            identify_image_callback=self.identify_image_maunally
        )
        return resp.text

    # this is not used
    def fetch_article(self,
                      keyword,
                      page=1,
                      period=SearchArticleTime.ANYTIME,
                      article_type = SearchArticleType.ALL):
        url = SogouRequest.generate_search_article_url(
            keyword, page, period, article_type)
        resp = self.__get_and_unlock(url,
                                     unlock_function=self.__unlock_wechat,
                                     identify_image_callback=self.identify_image_maunally)
        return Parser.parse_article(resp.text)

    def fetch_gzh_info(self, keyword):
        url = SogouRequest.generate_search_gzh_url(keyword)
        resp = self.__get_and_unlock(url,
                                     self.__unlock_sogou,
                                     self.identify_image_maunally)
        return Parser.parse_gzh(resp.text)

    def fetch_history_urls_from_profile(self, profile_url):
        resp = self.__get_and_unlock(profile_url,
                                     unlock_function=self.__unlock_wechat,
                                     identify_image_callback=self.identify_image_maunally)
        return Parser.parse_urls_from_profile(resp.text)

    def __get(self, url, session):
        resp = session.get(url)
        retry = 0
        while not resp.ok and retry < self.retries:
            resp = session.get(url)
            retry += 1
        if not resp.ok:
            raise SogouCrawlerRequestsException('no response at __get', resp)
        return resp

    def __get_and_unlock(self, url, unlock_function, identify_image_callback):
        session = requests.session()
        resp = self.__get(url, session)

        if 'antispider' in resp.url or u'请输入验证码' in resp.text:
            unlock_function(url, resp, session, identify_image_callback)
            resp = self.__get(url, session)
        return resp

    def __unlock_sogou(self, url, resp, session, identify_image_callback=None):
        millis = int(round(time.time() * 1000))  # round?
        r_cap = session.get('http://weixin.sogou.com/antispider/util/seccode.php?tc=%s' % millis)
        if not r_cap.ok:
            raise SogouCrawlerRequestsException('no response at __unlock_sogou', resp)
        r_unlock = self.unlock_sogou_callback(url, session, resp, r_cap.content, identify_image_callback)

        if r_unlock['code'] != 0:
            raise SogouCrawlerRequestsException('Verification code failed: code %s, msg %s' %
                            (r_unlock.get('code'), r_unlock.get('msg')))

    def __unlock_wechat(self, url, resp, session, identify_image_callback=None):
        r_cap = session.get('https://mp.weixin.qq.com/mp/verifycode?cert=%s' % (time.time() * 1000))
        if not r_cap.ok:
            raise SogouCrawlerRequestsException('SogouAPI unlock_history get img failed', resp)

        r_unlock = self.unlock_wechat_callback(url, session, resp, r_cap.content, identify_image_callback)

        if r_unlock['ret'] != 0:
            raise SogouCrawlerRequestsException(
                '[SogouAPI identify image] code: %s, msg: %s, cookie_count: %s' % (
                    r_unlock.get('ret'), r_unlock.get('errmsg'), r_unlock.get('cookie_count')))

    def unlock_sogou_callback(self, url, req, resp, img, identify_image_callback):
        url_quote = url.split('weixin.sogou.com/')[-1]
        unlock_url = 'http://weixin.sogou.com/antispider/thank.php'
        data = {
            'c': identify_image_callback(img),
            'r': '%2F' + url_quote,
            'v': 5
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://weixin.sogou.com/antispider/?from=%2f' + url_quote
        }
        r_unlock = req.post(unlock_url, data, headers=headers)
        if not r_unlock.ok:
            raise SogouCrawlerRequestsException('Sogou url unlock failed')

    def unlock_wechat_callback(self, url, req, resp, img, iden_image_callback):
        unlock_url = 'https://mp.weixin.qq.com/mp/verifycode'
        data = {
            'cert': time.time() * 1000,
            'input': iden_image_callback(img)
        }
        headers = {
            'Host': 'mp.weixin.qq.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        r_unlock = req.post(unlock_url, data, headers=headers)
        if not r_unlock.ok:
            raise SogouCrawlerRequestsException('Wechat url unlock failed')
        return r_unlock.json()

    def show_img(self, content):
        f = tempfile.TemporaryFile()
        f.write(content)
        return Image.open(f)

    def identify_image_maunally(self, img):
        im = self.show_img(img)
        im.show()
        return raw_input('pls input code: ')


if __name__ == '__main__':
    api = SogouAPI()
    info = api.fetch_gzh_info(keyword='九章算法')

    if 'profile' in info[0]['profile_url']:
        articles = api.fetch_history_urls_from_profile(info[0]['profile_url'])
        f = open(u'../Content/%s' % info[0]['wechat_id'], 'a')
        f.write(json.dumps(articles).encode('utf-8'))
        f.close()

        for article in articles:
            print article
