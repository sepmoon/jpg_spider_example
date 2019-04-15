#! /usr/bin/env python
# -*- coding: utf-8 -*-


from concurrent.futures import ThreadPoolExecutor, wait
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

    def get_pic_url(self, url):
        """
        获取目标URL可下载列表
        """
        if re.search(r'http://|https://', str(url)):
            if len(re.split(r'://|/', str(url))) == 2:
                url = str(url) + '/'
            lists_ = []
            new_con = self.con.request('GET', url, headers=self.header)
            con_data = new_con.data.decode('utf-8')
            list_ = self.regulars.findall(con_data)
            for num in range(len(list_)):
                try:
                    list_str = list_[num].split('="')[1]
                    if re.search(r'http://|https://', list_str):
                        lists_.append("{}".format(list_str))
                    else:
                        re_url = re.split(r'://|/', url)
                        lists_.append("{s1}://{s2}{s3}".format(s1=re_url[0], s2=re_url[1], s3=list_str))
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

    def _get_pic(self, url):
        if url:
            pic_name = re.split(r'//|/', url)[-1].split('.')
            fo = open('{}-.{}'.format(pic_name[0], pic_name[1]), 'wb')
            dpic = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            result = dpic.request('GET', url, headers=self.header)
            fo.write(result.data)
            fo.close()
        else:
            print("没有可用下载链接")


if __name__ == '__main__':
    start_time = time.time()
    run = GetPicDownload()
    run.download_pic('http://www.nipic.com/')
    finish_time = time.time() - start_time
    print(finish_time)
