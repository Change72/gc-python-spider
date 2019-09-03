import time
import json
import random
import requests
import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from methods.db_method import DB_Connection
from methods.my_logger import logger


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

class Wenshu(object):
    def __init__(self):
        self.log = logger()
        self.all_types = ['刑事案件', '民事案件', '行政案件', '赔偿案件', '执行案件']
        self.options = Options()
        self.options.headless = False
        self.firefox_profile = webdriver.FirefoxProfile()
        self.expire_time = "2000-01-01 00:00:00"

    def update_proxy(self):
        if datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") > self.expire_time:
            ip_proxy = self.get_ip()
            if ip_proxy:
                ip, port, self.expire_time = ip_proxy

                # Direct = 0, Manual = 1, PAC = 2, AUTODETECT = 4, SYSTEM = 5
                self.firefox_profile.set_preference("network.proxy.type", 1)
                self.firefox_profile.set_preference("network.proxy.http", ip)
                self.firefox_profile.set_preference("network.proxy.http_port", int(port))
                self.firefox_profile.set_preference("network.proxy.ssl", ip)
                self.firefox_profile.set_preference("network.proxy.ssl_port", int(port))
                self.firefox_profile.set_preference("general.useragent.override", "whater_useragent")
                self.firefox_profile.update_preferences()
                return


    def get_ip(self):
        with open('./configuration.json') as f:
            data = json.load(f)
            url = data['DynamicProxyIP']
        ip_text = requests.get(url).text
        ip_json = json.loads(ip_text)
        if ip_json['code'] == 0:
            return ip_json['data'][0]['ip'], ip_json['data'][0]['port'], ip_json['data'][0]['expire_time']
        return None

    def scan_case(self, url):
        # self.update_proxy()
        browser = webdriver.Firefox(options=self.options, firefox_profile=self.firefox_profile)
        browser.implicitly_wait(10)
        browser.get(url)
        browser.set_window_size(1500,3000)
        time.sleep(random.uniform(5, 10))
        categories = browser.find_elements_by_xpath('//li/a[@class="case"]')
        for i, column in enumerate(categories):
            if i > 4:
                break
            else:
                ActionChains(browser).move_to_element(column).click().perform()

            time.sleep(random.uniform(3, 5))
            handles = browser.window_handles
            browser.switch_to.window(handles[1])

            # order_icon = browser.find_element_by_xpath('//div[@data-value="s51"]')
            # ActionChains(browser).move_to_element(order_icon).click().perform()
            #
            advenced_search_icon = browser.find_element_by_xpath('//div[@class="advenced-search"]')
            ActionChains(browser).move_to_element(advenced_search_icon).click().perform()

            start_input = browser.find_element_by_id("cprqStart")
            ActionChains(browser).send_keys("2019-08-29").perform()
            end_input = browser.find_element_by_id("cprqEnd")
            ActionChains(browser).send_keys("change0702@126.com").perform()
            ActionChains(browser).move_to_element(browser.find_element_by_id("searchBtn")).click().perform()



            time.sleep(random.uniform(3, 5))
            page_num = 1
            while True:
                self.log.info("类别 " + str(i) + " 第 " + str(page_num) + " 页开始")
                time.sleep(random.uniform(3, 5))
                case_blocks = browser.find_elements_by_xpath('//div[@class="LM_list"]')
                for k, case in enumerate(case_blocks):
                    self.item = Item()
                    self.item.case_type = self.all_types[i]
                    self.item.doc_type = case.find_element_by_xpath('./div/div[@class="labelTwo"]').text
                    self.item.pun_title = case.find_element_by_xpath('./div/h4/a').text
                    self.item.pun_org = case.find_element_by_xpath('./div/span[@class="slfyName"]').text
                    self.item.doc_id = case.find_element_by_xpath('./div/span[@class="ah"]').text
                    self.item.doc_date = case.find_element_by_xpath('./div/span[@class="cprq"]').text
                    self.item.id = case.find_element_by_xpath('./div/a/input').get_attribute('data-value')
                    self.item.file_path = 'http://wenshu.court.gov.cn/website/wenshu/181107ANFZ0BXSK4/index.html?docId=' + self.item.id

                    db = DB_Connection()
                    db.open_connection()
                    insert_result = db.save_list_info(self.item)
                    db.close_connection()

                    if not insert_result:
                        # 数据库中已存在，不获取详情页
                        continue

                    ActionChains(browser).move_to_element(case.find_element_by_xpath('./div/h4/a')).click().perform()
                    time.sleep(random.uniform(3, 5))
                    handles = browser.window_handles
                    browser.switch_to.window(handles[2])

                    self.item.pub_date = browser.find_element_by_xpath('//td[@style="text-align:left;width:33%;padding-left:30px;border:0px solid #ccc"]').text[5:]
                    pub_fact = browser.find_element_by_xpath('//div[@class="PDF_pox"]')
                    self.item.pun_fact = pub_fact.text
                    if self.item.doc_id == "":
                        self.item.doc_id = browser.find_element_by_id('1').text

                    db = DB_Connection()
                    db.open_connection()
                    db.save_details(self.item)
                    db.close_connection()

                    browser.close()
                    browser.switch_to.window(handles[1])

                    self.log.info("类别 " + str(i) + " 第 " + str(page_num) + " 页第 " + str(k) + "项完成")

                    time.sleep(random.uniform(3, 5))

                time.sleep(random.uniform(3, 5))

                page_num += 1
                if page_num > 40:
                    break
                next_page_icon = browser.find_element_by_xpath('//a[@value="' + str(page_num) + '"]')
                ActionChains(browser).move_to_element(next_page_icon).click().perform()

            browser.close()
            browser.switch_to.window(handles[0])

        browser.quit()
        return True


    def supply_facts(self):
        db = DB_Connection()
        db.open_connection()
        db.identify_unfinished()
        unfinished_items = db.get_unfinish_detail()
        db.clear_finished()

        self.update_proxy()
        browser = webdriver.Firefox(options=self.options, firefox_profile=self.firefox_profile)
        browser.implicitly_wait(5)
        browser.set_window_size(1500,3000)
        time.sleep(random.uniform(5, 10))

        for doc_id in unfinished_items:
            browser.get(doc_id[2])
            browser.implicitly_wait(10)
            time.sleep(random.uniform(1, 5))

            self.item = Item()
            self.item.id = doc_id[0]
            self.item.doc_id = doc_id[1]
            self.item.pub_date = browser.find_element_by_xpath(
                '//td[@style="text-align:left;width:33%;padding-left:30px;border:0px solid #ccc"]').text[5:]
            pub_fact = browser.find_element_by_xpath('//div[@class="PDF_pox"]')
            self.item.pun_fact = pub_fact.text
            if self.item.doc_id == "":
                self.item.doc_id = browser.find_element_by_id('1').text

            db = DB_Connection()
            db.open_connection()
            db.save_details(self.item)
            db.close_connection()

        browser.quit()


if __name__ == '__main__':
    url = "http://wenshu.court.gov.cn/"
    while True:
        try:
            spider = Wenshu()
            spider.scan_case(url=url)
            spider.supply_facts()
        except Exception as e:
            print(e)















