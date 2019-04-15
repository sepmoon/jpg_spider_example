#! /usr/bin/env python
# -*- coding: utf-8 -*-


from concurrent.futures import ThreadPoolExecutor, wait
import certifi  # 证书认证
import urllib3
import re


class GetPicDownload():
    """
    访问目标URl页面，抓取图片链接并下载到本地路径
    """

    def __init__(self):
        self.header = urllib3.make_headers(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15')
        self.regulars = re.compile(r'src=.+\.jpg|src=.+\.png')
        self.con = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())  # 设置证书认证

    def getPicUrl(self, url):
        """
        获取目标URL可下载列表
        :param url:
        :return:
        """
        if re.search(r'http://|https://', str(url)):
            if len(re.split(r'://|/', str(url))) == 2:
                url = str(url) + '/'
            reLists = []
            new_con = self.con.request('GET', url, headers=self.header)
            con_data = new_con.data.decode('utf-8')
            reList = self.regulars.findall(con_data)
            for num in range(len(reList)):
                try:
                    list_str = reList[num].split('="')[1]
                    if re.search(r'http://|https://', list_str):
                        reLists.append("{}".format(list_str))
                    else:
                        re_url = re.split(r'://|/', url)
                        reLists.append("{s1}://{s2}{s3}".format(s1=re_url[0], s2=re_url[1], s3=list_str))
                except BaseException:
                    pass
            reLists = list(dict.fromkeys(reLists).keys())  # 提取图片链接去重，返回一个列表

            return reLists
        else:
            return ("Error,Please check input the url.\nExample URL: https://www.google.com")

    def downLoadPic(self, url):
        """
        调用线程池去执行_getPic方法下载
        :param url:
        :return:
        """
        picLists = self.getPicUrl(url)
        if picLists:
            executor = ThreadPoolExecutor(max_workers=3)
            all_task = [executor.submit(self._getPic, url) for url in picLists]
            wait(all_task)
            print('All Download Finish.')

    def _getPic(self, url):
        if url:
            picName = re.split(r'//|/', url)[-1].split('.')
            fo = open('{}-.{}'.format(picName[0], picName[1]), 'wb')
            dpic = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            result = dpic.request('GET', url, headers=self.header)
            fo.write(result.data)
            fo.close()
        else:
            print("没有可用下载链接")


run = GetPicDownload()
run.downLoadPic('http://www.nipic.com/')
