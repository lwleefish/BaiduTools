"""
    "avg":2953782, #日均
    "yoy":25,      #同比
    "qoq":-23      #环比
"""
import requests
import json
from urllib.parse import quote


class BaiduIndex(object):
    """百度指数获取, 默认全国范围"""
    def __init__(self, BDUSS):
        """初始化
        :param BDUSS: a value in cookie str
        """
        self._bduss = BDUSS
        self._key_dict = dict()
        self._ajax_header = {
            "Cookie": "BDUSS=" + self._bduss, 
            "Referer": "http://index.baidu.com/v2/main/index.html", 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36", 
            "X-Requested-With": "XMLHttpRequest"
        }

    def _decrypt(self, key, data):
        """指数解密"""
        a = dict()
        r = list()
        mid = len(key) // 2
        for o in range(mid):
            a[key[o]] = key[mid + o]
        for s in range(len(data)):
            r.append(a[data[s]])
        return "".join(r)
    
    def _get_index(self, url):
        rsp_index = requests.get(url, headers=self._ajax_header)
        rsp_index.encoding = "utf-8"
        if not rsp_index:
            return
        index = json.loads(rsp_index.text)    
        uniqid = index['data']['uniqid']
        if uniqid not in self._key_dict:
            rsp_key = requests.get("http://index.baidu.com/Interface/ptbk?uniqid=" + uniqid, headers=self._ajax_header)
            key_json = json.loads(rsp_key.text)
            key = key_json["data"]
            self._key_dict.clear()
            self._key_dict[uniqid] = key
        else:
            key = self._key_dict[uniqid]
        if not key:
            return None
        return key, index
    
    def get_feed_index(self, keywords: str, days: int=30, startDate: str=None, endDate: str=None):
        r"""获取关键词资讯指数
    
        :param keywords: 搜索词,如果有多个用逗号分隔, 最多不超过5个, 如：特朗普,奥巴马 str
        :param days: 要搜索的天数 int
        :param startDate: 搜索起始日期(当起始日期和结束日期不为空时days无效, 否则起始结束日期无效) str
        :param endDate: 搜索起始日期(当起始日期和结束日期不为空时days无效, 否则起始结束日期无效) str 
        """
        if not startDate or not endDate:
            day_param = "days=%d" % days
        else:
            day_param = "startDate=%s&endDate=%s" % (startDate, endDate)
        url = "http://index.baidu.com/api/FeedSearchApi/getFeedIndex?area=0&word=%s&%s" % (quote(keywords), day_param)
        key, index = self._get_index(url)
        cnt = len(index['data']['index'])
        for idx in range(cnt):
            data = index['data']['index'][idx]['data']
            index['data']['index'][idx]['data'] = self._decrypt(key, data)
        return index['data']['index']
    
    def get_search_index(self, keywords: str, days: int=30, startDate: str=None, endDate: str=None):
        """ 获取关键词百度搜索指数
    
        :param keywords: 搜索词,如果有多个用逗号分隔, 最多不超过5个, 如：特朗普,奥巴马 str
        :param days: 要搜索的天数 int
        :param startDate: 搜索起始日期(当起始日期和结束日期不为空时days无效, 否则起始结束日期无效) str
        :param endDate: 搜索起始日期(当起始日期和结束日期不为空时days无效, 否则起始结束日期无效) str 
        """
        if not startDate or not endDate:
            day_param = "days=%d" % days
        else:
            day_param = "startDate=%s&endDate=%s" % (startDate, endDate)
        url = "http://index.baidu.com/api/SearchApi/index?area=0&word=%s&%s" % (quote(keywords), day_param)
        key, index = self._get_index(url)
        cnt = len(index['data']['userIndexes'])
        for idx in range(cnt):
            all_data = index['data']['userIndexes'][idx]['all']['data']
            index['data']['userIndexes'][idx]['all']['data'] = self._decrypt(key, all_data)
            pc_data = index['data']['userIndexes'][idx]['pc']['data']
            index['data']['userIndexes'][idx]['pc']['data'] = self._decrypt(key, pc_data)
            wise_data = index['data']['userIndexes'][idx]['wise']['data']
            index['data']['userIndexes'][idx]['wise']['data'] = self._decrypt(key, wise_data)
            index['data']['userIndexes'][idx]['generalRatio'] = index['data']['generalRatio'][idx]
        return index['data']['userIndexes']
    
    def get_news_index(self, keywords: str, days: int=30, startDate: str=None, endDate: str=None)-> dict:
        """获取媒体指数
    
        :param keywords: 搜索词,如果有多个用逗号分隔, 最多不超过5个, 如：特朗普,奥巴马 str
        :param days: 要搜索的天数 int
        :param startDate: 搜索起始日期(当起始日期和结束日期不为空时days无效, 否则起始结束日期无效) str
        :param endDate: 搜索起始日期(当起始日期和结束日期不为空时days无效, 否则起始结束日期无效) str 
        """
        if not startDate or not endDate:
            day_param = "days=%d" % days
        else:
            day_param = "startDate=%s&endDate=%s" % (startDate, endDate)
        url = "http://index.baidu.com/api/NewsApi/getNewsIndex?area=0&word=%s&%s" % (quote(keywords), day_param)
        key, index = self._get_index(url)
        cnt = len(index['data']['index'])
        for idx in range(cnt):
            data = index['data']['index'][idx]['data']
            index['data']['index'][idx]['data'] = self._decrypt(key, data)
        return index['data']['index']

    def get_hot_news(self, keywords: str, *dates: tuple):
        """获取关键词 指定日期热点新闻
        
        :param keywords: 搜索词,如果有多个用逗号分隔, 最多不超过5个, 如：特朗普,奥巴马 str
        :param dates: 日期 tuple<str>
        :return 新闻字典对象 
        """
        date = ",".join(dates)
        raw_date = date
        for i in range(1, len(keywords.split(","))):
            date = date + "&dates[]=" + raw_date
        url = "http://index.baidu.com/api/NewsApi/checkNewsIndex?dates[]=%s&type=day&words=%s" % (date, quote(keywords))
        print(url)
        rsp = requests.get(url, headers=self._ajax_header)
        rsp.encoding = "utf-8"
        data = json.loads(rsp.text)
        return data
    
    def get_social_distribution(self, startDate: str, endDate: str, *keywords: tuple):
        """人群分布
        "<=19, 20~29, 30~39, 40~49, >=50
        param startDate: 开始月份如：20190601 
        param endDate: 开始月份如：20190601 
        param keyword: 搜索关键词
        """
        keys = "&wordlist[]=".join(keywords)
        url = "http://index.baidu.com/api/SocialApi/getSocial?wordlist[]=%s&startdate=%s&enddate=%s" % (keys, startDate, endDate)
        rsp = requests.get(url, headers=self._ajax_header)
        rsp.codeing = "utf-8"
        data = json.loads(rsp.text)
        return data

    def get_social_interest(self, typeid: str="", *keywords: tuple):
        """兴趣分布 TGI"""
        keys = "&wordlist[]=".join(keywords)
        url = "http://index.baidu.com/api/SocialApi/getSocial?wordlist[]=%s&typeid=%s&callback=%s" % (keys, typeid, "jsonp1")
        rsp = requests.get(url, headers=self._ajax_header)
        rsp.codeing = "utf-8"
        res = rsp.text[len("jsonp1("):-1]
        data = json.loads(res)
        return data
    
    def get_region(self, startDate: str, endDate: str, *keywords: tuple):
        """地域分布"""
        keys = "&wordlist[]=".join(keywords)
        url = "http://index.baidu.com/api/SearchApi/region?region=0&word=%s&startDate=%s&endDate=%s" % (keys, startDate, endDate)
        rsp = requests.get(url, headers=self._ajax_header)
        rsp.codeing = "utf-8"
        data = json.loads(rsp.text)
        return data