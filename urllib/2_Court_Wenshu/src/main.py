import re
import requests
import copy
import random
import datetime

from methods.db_method import DB_Connection
from methods.docid import getkey, decode_docid
from methods.js_method import ParseJs, ParseDetail, Para
from methods.my_logger import logger
from lxml import etree

'''
文书网爬虫：http://wenshu.court.gov.cn/
按五大门类，目前对列表页循环访问
Refer to: https://github.com/Monster2848/caipanwenshu
Author: Change
2019-08
'''
class Wenshu(object):
    def __init__(self, proxies, start_time, end_time, case_type_number, target_page):
        self.log = logger()
        self.all_types = ['刑事案件', '民事案件', '行政案件', '赔偿案件', '执行案件']
        self.case_type_number = case_type_number
        self.target_page = target_page
        self.start_time = start_time
        self.end_time = end_time
        # self.proxy = {'https':'http://127.0.0.1:1080'}
        self.proxy = proxies
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Encoding': 'gzip, deflate',
                       'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                       'Upgrade-Insecure-Requests': '1',
                       'Cache-Control': 'max-age=0',
                       'Connection': 'keep-alive',
                       'User-Agent': Para().get_user_agent(),
                        }


    # 列表页第一次
    def list_1(self):
        # url = 'http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+++'+ self.start_time + ' TO ' \
        #       + self.end_time + '+上传日期:' + self.start_time + ' TO ' + self.end_time + '&conditions=searchWord ' + \
        #       str(self.case_type_number + 1) + ' AJLX 案件类型:' + self.all_types[self.case_type_number] + 'HTTP/1.1'
        url = 'http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord ' + str(self.case_type_number + 1) \
              + ' AJLX 案件类型:' + self.all_types[self.case_type_number] + 'HTTP/1.1'
        try:
            resp = requests.get(
                url=url,
                headers=self.headers,
                proxies=self.proxy,
                allow_redirects=False,
                timeout=60
            )
            # 修改requests的编码，在resp中的 apparent_encoding 有提示
            resp.encoding = 'UTF-8-SIG'

            vjkl5 = re.search('vjkl5=(.*?); ', resp.headers._store['set-cookie'][1]).group(1)
        except Exception as e:
            self.log.error(e)
            return None
        return vjkl5, url

    # 列表页第二次
    def list_2(self):
        # 列表页第一次的5次尝试
        vjkl5 = None
        for i in range(5):
            package = self.list_1()
            if not package:
                continue
            vjkl5, old_url = package
            break

        if not vjkl5:
            self.log.warning(self.all_types[self.case_type_number] + str(self.target_page) + '列表页第一次失败')
            return None
        # 解析
        vl5x, guid = ParseJs().get_key_para(vjkl5)
        url = "http://wenshu.court.gov.cn/List/ListContent"
        data = {
            # "Param": '上传日期:' + self.start_time + ' TO ' + self.end_time + ',案件类型:' + self.all_types[self.case_type_number],
            "Param": '案件类型:' + self.all_types[self.case_type_number],
            "Index": self.target_page,  # 这里是页数
            # "Page": 10,  # 这个不变
            "Page": 10,  # 这个不变
            # "Order": "法院层级",  # 排序关键词
            "Order": "裁判日期",  # 排序关键词
            # "Direction": "asc",  # 排序方向
            "Direction": "desc",  # 排序方向
            "number": "wens",
            "vl5x": vl5x,
            # "guid": guid
        }

        list_headers = copy.deepcopy(self.headers)
        list_headers["X-Requested-With"] = "XMLHttpRequest"
        list_headers["Host"] = "wenshu.court.gov.cn"
        list_headers["Referer"] = old_url.encode('utf-8')
        list_headers["Origin"] = "http://wenshu.court.gov.cn"
        list_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"

        try:
            resp = requests.post(
                url=url,
                headers=list_headers,
                proxies=self.proxy,
                allow_redirects=True,
                timeout=60,
                cookies={
                    "vjkl5": vjkl5,
                },
                data=data
            )
            resp.encoding = 'UTF-8-SIG'
        except Exception as e:
            self.log.error(e)
            return None

        return resp.text

    # 列表页解析
    def list_3(self):
        self.log.info("开始获取 类别" + str(self.case_type_number) + " 第 " + str(self.target_page) + "页")
        # 列表页第二次的20次尝试
        datalist = None
        for i in range(30):
            text = self.list_2()
            if not text:
                continue
            context = ParseDetail(text)
            datalist = context.parse_list_data()
            if datalist:
                break

        if not datalist:
            self.log.warning(self.all_types[self.case_type_number] + "列表第 " + str(self.target_page) + ' 页失败')
            return None

        RunEval = datalist[0]['RunEval']
        key = getkey(RunEval)

        for case in datalist[1:]:
            parse_obj = ParseDetail(case)
            title, court, pdate, writ, reason, Docid, process = parse_obj.parse_items()

            docid = decode_docid(Docid, key)

            self.item = Item()
            self.item.pun_title = title
            self.item.pun_org = court
            self.item.doc_date = pdate
            self.item.doc_id = writ
            # self.item.pun_fact = reason
            self.item.id = docid
            self.item.case_type = self.all_types[self.case_type_number]
            self.item.doc_type = self.all_types[self.case_type_number][:2] + process
            self.item.file_path = 'http://wenshu.court.gov.cn/content/content?DocID=' + docid + '&KeyWord='

            db = DB_Connection()
            db.open_connection()
            insert_result = db.save_list_info(self.item)
            db.close_connection()

            if not insert_result:
                # 数据库中已存在，不获取详情页
                continue

            for i in range(100):
                detail_html = self.detail(docid)
                if detail_html:
                    context = ParseDetail(detail_html)
                    html_result = context.parse_detail()
                    if not html_result:
                        continue
                    html_raw, pub_date, case_num = html_result
                    response = etree.HTML(text=html_raw.replace('\t', ''))
                    response_list = response.xpath('//div')
                    new_text = " ".join([x.xpath('string(.)').replace(u'\u3000', '') for x in response_list])

                    self.item.pub_date = pub_date
                    if case["不公开理由"] != '':
                        self.item.pun_fact = "不公开理由：" + new_text
                    else:
                        self.item.pun_fact = new_text
                    if self.item.doc_id == "":
                        self.item.doc_id = case_num

                    db = DB_Connection()
                    db.open_connection()
                    db.save_details(self.item)
                    db.close_connection()

                    break

        db = DB_Connection()
        db.open_connection()
        db.update_finished(self.case_type_number, self.target_page)
        db.close_connection()
        print()

    def parse_detail(self, docid):
        self.item = Item()
        self.item.id = docid
        for i in range(100):
            detail_html = self.detail(docid)
            if detail_html:
                context = ParseDetail(detail_html)
                html_result = context.parse_detail()
                if not html_result:
                    continue
                html_raw, pub_date, case_num = html_result
                response = etree.HTML(text=html_raw.replace('\t',''))
                response_list = response.xpath('//div')
                new_text = " ".join([x.xpath('string(.)').replace(u'\u3000', '') for x in response_list])
                self.item.pub_date = pub_date
                self.item.pun_fact = new_text
                if self.item.doc_id == "":
                    self.item.doc_id = case_num

                db = DB_Connection()
                db.open_connection()
                db.save_details(self.item)
                db.close_connection()
                break
        return

    def detail(self, docid):
        url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=' + docid
        try:
            resp = requests.get(
                url=url,
                headers=self.headers,
                proxies=self.proxy,
                allow_redirects=False,
                timeout=60,
            )
        except Exception as e:
            self.log.error(e)
            return None
        return resp.text


class Item(object):
    def __init__(self):
        self.id = ""        # docid
        self.doc_id = ""    # 官网显示的判决文书号
        self.doc_date = ""
        self.pub_date = ""
        self.pun_org = ""
        self.pun_fact = ""
        self.case_type = "" # 五个大类
        self.doc_type = ""  # 案件小类
        self.pun_title = ""
        self.file_path = ""


if __name__ == '__main__':
    start_time = (datetime.datetime.now() + datetime.timedelta(days=0)).strftime("%Y-%m-%d")
    end_time = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    proxies = {}
    expire_time = "2000-01-01 00:00:00"

    db = DB_Connection()
    db.open_connection()
    unfinished_pages = db.get_unfinish_page()
    db.close_connection()
    random_list = list(range(len(unfinished_pages)))
    random.shuffle(random_list)
    while True:
        for cell in random_list:
            if datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") > expire_time:
                ip_proxy = Para().get_ip()
                if ip_proxy:
                    ip, port, expire_time = ip_proxy
                    proxies['https'] = "http://" + str(ip) + ':' + str(port)
                else:
                    continue
            print(unfinished_pages[cell][0], unfinished_pages[cell][1])
            spider = Wenshu(proxies, start_time, end_time, unfinished_pages[cell][0], unfinished_pages[cell][1])
            spider.list_3()


        db = DB_Connection()
        db.open_connection()
        unfinished_items = db.get_unfinish_detail()
        for docid in unfinished_items:
            spider = Wenshu(None, start_time, end_time, 0, 1)
            spider.parse_detail(docid[0])
        db.clear_finished()
        unfinished_pages = db.get_unfinish_page()
        random_list = list(range(len(unfinished_pages)))
        random.shuffle(random_list)
        db.close_connection()

