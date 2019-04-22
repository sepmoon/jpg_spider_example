#! /usr/bin/env python
# -*- coding: utf-8 -*-


from concurrent.futures import ThreadPoolExecutor, wait
from urllib3.util.url import parse_url
import certifi  # 证书认证
import urllib3
import re
import time


class GetPicDownload:
    """
    访问目标URl页面，抓取图片链接并下载到本地路径
    """

    def __init__(self):
        self.header = urllib3.make_headers(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:66.0) Gecko/20100101 Firefox/66.0')
        self.regulars = re.compile(r'src=.+\.jpg|src=.+\.png')
        self.con = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())  # 设置证书认证
        self.urls = None

    @staticmethod
    def _url_testing(url):
        scheme_ = parse_url(url).scheme
        if scheme_ == 'http' or scheme_ == 'https':
            return True
        else:
            return False

    @staticmethod
    def _get_pic_name(url):
        return re.split(r'//|/', url)[-1].split('.')

    def _get_pic(self, url):
        if url:
            result = self.con.request('GET', url, headers=self.header)
            if result.data:
                pic_name = self._get_pic_name(url)
                fo = open('{}-.{}'.format(pic_name[0], pic_name[1]), 'wb')
                fo.write(result.data)
                fo.close()
        else:
            print("没有可用下载链接")

    def get_pic_url(self, url):
        """
        获取目标URL可下载列表
        """
        if self._url_testing(url):
            self.urls = parse_url(url)
            lists_ = []
            new_con = self.con.request('GET', url, headers=self.header)
            con_data = new_con.data.decode('utf-8')
            list_ = self.regulars.findall(con_data)
            for num in range(len(list_)):
                try:
                    list_str = list_[num].split('="')[1]
                    if self._url_testing(list_str):
                        lists_.append("{}".format(list_str))
                    else:
                        lists_.append("{s1}://{s2}{s3}".format(s1=self.urls.scheme, s2=self.urls.host, s3=list_str))
                except BaseException:
                    pass
            lists_ = list(dict.fromkeys(lists_).keys())  # 提取图片链接去重，返回一个列表

            return lists_
        else:
            return "Error,Please check input the url.\nExample URL: https://www.google.com"

    def download_pic(self, url):
        """
        调用线程池去执行_get_pic方法下载
        """
        pic_lists = self.get_pic_url(url)
        if pic_lists:
            executor = ThreadPoolExecutor(max_workers=3)
            all_task = [executor.submit(self._get_pic, url) for url in pic_lists]
            wait(all_task)
            print('All Download Finish.')


if __name__ == '__main__':
    start_time = time.time()
    run = GetPicDownload()
    run.download_pic('http://www.nipic.com')
    finish_time = time.time() - start_time
    print(finish_time)
