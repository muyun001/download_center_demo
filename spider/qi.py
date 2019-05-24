# coding:utf-8
import codecs
import re
import uuid
import urllib
import lxml.html
import traceback
from bs4 import BeautifulSoup
# from lxml import etree
import cssselect
import time
import requests
# from selenium import webdriver
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Qichacha():

    def __init__(self):
        # self.webdriver = webdriver.Chrome(executable_path = 'chromedriver.exe')  # 使用谷歌浏览器
        self.save_path = r'./data/data/'
        self.keyword = '网络营销'
        self.url = 'https://www.qichacha.com/search?key={}'.format(urllib.quote(self.keyword))
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': 'QCCSESSID=8m6kegjp03th6229it1pcunit4; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1550824144; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1550806981; acw_tc=deba959a15509973585838752e7c53d2eb8f2aca187144e5afac10096e; zg_did=%7B%22did%22%3A%20%221691ea5b3d2648-0a1880b1bb3978-1333062-1fa400-1691ea5b3d3a8d%22%7D; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1550806981; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201551004144921%2C%22updated%22%3A%201551008405387%2C%22info%22%3A%201550997369815%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.qichacha.com%22%2C%22cuid%22%3A%20%222456025febed0b27b4c50e3177c776bc%22%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1551008405',
            'Host': 'www.qichacha.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }
        self.sec_headers = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'QCCSESSID=8m6kegjp03th6229it1pcunit4; acw_tc=3da0cc9e15508252687751941ea7d8bd80753df0dc0bb6edc83380e2a5; zg_did=%7B%22did%22%3A%20%221691463a8591c-0c0259cccd35cd-1333062-1fa400-1691463a85a63e%22%7D; hasShow=1; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1550806981; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201550825269342%2C%22updated%22%3A%201550826568948%2C%22info%22%3A%201550825269344%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%2C%22cuid%22%3A%20%222456025febed0b27b4c50e3177c776bc%22%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1550826569',
            'Host': 'www.qichacha.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.province_list = ['AH','BJ','CQ','FJ','GD','GS','GX','GZ','HAIN','HB','HEN','HK','HLJ','HUB','HUN','JL','JS','JX','LN','NMG','NX','QH','SAX','SC','SD','SH','SX','TJ','XJ','XZ','YN','ZJ','CN']
        # self.province_list = ['AH']

    def get_com_num(self, url, headers):
        '''获取查询到的企业个数'''
        response = requests.get(url, headers=headers, allow_redirects=False)
        if response.status_code != 200:
            return
        tree = lxml.html.fromstring(response.text)
        num_obj = tree.cssselect('span.font-15 span,text-danget')
        if len(num_obj) != 0:
            com_num = num_obj[0].text.strip()
            if com_num == '':  # 没查到数据
                return None
            return int(com_num)
        else:
            return None

    # def get_province_pinyin(self):
    #     '''获取所有省份的拼音列表'''
    #     with open('./data/province_pinyin.txt', 'r') as f:
    #         province_pinyin_list = f.readlines()
    #     return province_pinyin_list


    def get_city_list(self, province):
        '''获取某省份下城市的编号列表'''
        url = 'https://www.qichacha.com/search_getCityListHtml?province={}&q_type=1'.format(province)
        response = requests.get(url, headers=self.headers, allow_redirects=False)
        if response.status_code != 200:
            return
        city_id_list = re.findall('data-value="(.*?)"', response.text, re.S)
        return city_id_list


    def get_district_list(self, city_id):
        '''获取某城市的所有地区列表'''
        url = 'https://www.qichacha.com/search_getCountyListHtml?city={}&q_type=1'.format(city_id)
        response = requests.get(url, headers=self.headers, allow_redirects=False)
        if response.status_code != 200:
            return
        district_list = re.findall('data-value="(.*?)"', response.text, re.S)  # 地区
        return district_list


    def derive_data(self, url):
        '''导出数据'''
        try:
            url = url.replace('search', 'search_getExcel')
            response = requests.get(url, headers=self.headers, allow_redirects=False)
            if response.status_code != 200:
                return
            if response.text == u'{"success":true}':  # 导出成功
                print('derive data succeed !!!')
                return True
            else:
                print('derive data failed !!!')
                return False
        except:
            print('derive data error ', traceback.print_exc())


    def get_download_url_list(self):
        '''获取所有的下载链接'''
        try:
            download_url_list = []
            download_page_list = ['https://www.qichacha.com/user_download.shtml?p=1']

            start_url = 'https://www.qichacha.com/user_download'
            response = requests.get(start_url, headers=self.headers, allow_redirects=False)
            if response.status_code != 200:
                return
            tree = lxml.html.fromstring(response.text)
            page_list = tree.cssselect('ul.pagination a.num')
            for _ in page_list:
                download_page_list.append('https://www.qichacha.com' + _.get('href'))

            for url in download_page_list:
                response = requests.get(url, headers=self.headers, allow_redirects=False)
                if response.status_code != 200:
                    return
                tree = lxml.html.fromstring(response.text)
                url_obj = tree.cssselect('tbody#downloadlistOld td a')
                for _ in url_obj:
                    download_url_list.append(_.get('href'))
            return download_url_list
        except:
            print('get download url list error ', traceback.print_exc())


    # def download_excel(self, excel_url):
    #     '''下载数据'''
    #     try:
    #         # response = requests.get(excel_url, headers=self.headers, verify=False)
    #         response = requests.get(excel_url, headers=self.headers)
    #         path = self.save_path + '/' + excel_url.split('/')[-1]
    #         with open(path, "wb") as f:
    #             f.write(response.content)
    #     except:
    #         print('download excel error', traceback.print_exc())

    def get_page(self, url):
        '''获取总页数'''
        response = requests.get(url, headers=self.headers, allow_redirects=False)
        if response.status_code != 200:
            return
        tree = lxml.html.fromstring(response.text)
        page_list = tree.cssselect('a#ajaxpage')
        if page_list:
            page_item = page_list[-1]
            if u'>' == page_item.text:
                page_item = page_list[-2]
            page = re.findall('(\d*)', page_item.text)
            for i in page:
                if i:
                    page = int(i)
                    return page
        else:
            return 1

    def generate_documents(self, url):
        '''生成文档'''
        response = requests.get(url, headers=self.headers, allow_redirects=False)
        if response.status_code != 200:
            return
        path = self.save_path + str(uuid.uuid1()) + '.txt'
        with codecs.open(path, 'w', 'utf-8') as f:
            f.write(response.text)

    def page_doc(self, basic_url):
        '''对每页进行访问，并将网页下载下来'''
        page = self.get_page(basic_url)
        for i in range(1, page+1):
            url = basic_url + 'p={}'.format(i)
            print(url)
            try:
                self.generate_documents(url)
                time.sleep(5)
            except:
                pass


    def run(self):
        all_url_list = []

        establishment_date_list = ['2015-2019', '2010-2014', '2005-2009', '2000-2004', '1995-1999', '1990-1994', '1985-1989', '1980-1900']  # 发布日期列表
        fund_list = ['0-100', '100-200', '200-300', '300-400', '400-500', '500-1000', '1000-5000', '5000-10000']  # 注册资金

        province_date_list = []
        for province in self.province_list:   # 省份
            for date in establishment_date_list:  # 创建日期
                url = self.url + '&ajaxflag=1&province={}&startDate={}&tel=T&'.format(province.strip(), date)
                province_date_list.append(url)


        for a_url in province_date_list:
            print(a_url)
            com_num = self.get_com_num(a_url, self.headers)
            if com_num != None:
                if com_num > 5000:
                    for fund in fund_list:  # 细分注册资金
                        b_url = a_url + 'registfund={}&'.format(fund)
                        print(b_url)
                        com_num = self.get_com_num(b_url, self.headers)
                        if com_num and com_num > 5000:
                            city_id_list = self.get_city_list(re.findall('&province=(.*?)&', b_url)[0])
                            for city_id in city_id_list:  # 细分城市
                                c_url = b_url + 'city={}&'.format(city_id)
                                print(c_url)
                                com_num = self.get_com_num(c_url, self.headers)
                                if com_num != None:
                                    if com_num > 5000:
                                        district_id_list = self.get_district_list(city_id)  # 获取城市的所有地区id
                                        for district_id in district_id_list[1:]:  # 细分行政区
                                            d_url = c_url + 'county={}&'.format(district_id)
                                            print(d_url)
                                            com_num = self.get_com_num(d_url, self.headers)
                                            if com_num != None:
                                                if com_num > 5000:
                                                    all_url_list.append(d_url)
                                                    print('com num more than 5000', d_url)
                                                else:
                                                    all_url_list.append(d_url)
                                                    # self.page_doc(d_url)
                                            time.sleep(2)
                                    else:
                                        all_url_list.append(c_url)
                                        # self.page_doc(c_url)
                                time.sleep(2)
                        else:
                            all_url_list.append(b_url)
                            # self.page_doc(b_url)
                        time.sleep(2)
                else:
                    all_url_list.append(a_url)
                    # self.page_doc(a_url)
            time.sleep(2)

        with codecs.open('all_url_list.txt', 'w', 'utf-8') as f:
            f.write(str(all_url_list))

if __name__ == '__main__':
    qichacha = Qichacha()
    qichacha.run()
    # qichacha.page_doc('https://www.qichacha.com/search?key=%E7%BD%91%E7%BB%9C%E8%90%A5%E9%94%80&ajaxflag=1&province=AH&startDate=1980-1900&tel=T&registfund=0-100&city=340100&')
    # download_excel_url = 'http://report.qichacha.com/ReportEngine/20190224131954820547472498_15654199.xls'
    # qichacha.download_excel(download_excel_url)
    # qichacha.get_city_list('AH')
    # qichacha.get_district_list('340100')
    # url = 'https://www.qichacha.com/search_index?key=%25E7%25BD%2591%25E7%25BB%259C%25E8%2590%25A5%25E9%2594%2580&ajaxflag=1&province=GD&startDate=2014-2019&city=440100&county=440103&'
    # qichacha.derive_data(url)
    # qichacha.get_download_url_list()
    # url = 'https://www.qichacha.com/search_index?key=%25E7%25BD%2591%25E7%25BB%259C%25E8%2590%25A5%25E9%2594%2580&ajaxflag=1&p=1&registfund=0-500&startDate=2018&province=BJ&'
    # qichacha.get_page(url)
    # qichacha.generate_documents(url)