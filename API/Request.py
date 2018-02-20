# -*- coding: utf-8 -*-
from collections import OrderedDict
from urllib import urlencode

from Constants import (
    SearchArticleTime,
    SearchArticleType
)

_search_gzh = 1
_search_article = 2


class SogouRequest:

    def __init__(self):
        pass

    @classmethod
    def generate_search_article_url(cls, keyword, page,
                                    time=SearchArticleTime.ANYTIME, article_type=SearchArticleType.ALL):
        assert isinstance(page, int) and page > 0
        assert time in SearchArticleTime.__dict__.values()  # RT
        query = OrderedDict()
        query["type"] = _search_article  # RT these parameters
        query["page"] = page
        query["ie"] = "utf8"
        query["tsn"] = time
        query["query"] = keyword
        if article_type is SearchArticleType.ALL:
            query["interation"] = "%s,%s" % (SearchArticleType.IMAGE, SearchArticleType.VIDEO)
        else:
            query["interation"] = article_type
        return "http://weixin.sogou.com/weixin?%s" % urlencode(query)

    @classmethod
    def generate_search_gzh_url(cls, keyword, page=1):
        assert isinstance(page, int) and page > 0
        query = OrderedDict()
        query["type"] = _search_gzh  # RT these parameters
        query["page"] = page
        query["ie"] = "utf-8"
        query["query"] = keyword
        return "http://weixin.sogou.com/weixin?%s" % urlencode(query)

    @staticmethod
    def generate_hot_url(hot_type, page=1):
        assert isinstance(page, int) and page > 0
        return "http://weixin.sogou.com/wapindex/was/0612/wap_%s/%s.html" % (hot_type, page - 1)


if __name__ is "__main__":
    url = SogouRequest.generate_search_gzh_url('九章算法')
    print url
