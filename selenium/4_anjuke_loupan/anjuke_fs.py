import requests
import pandas as pd
from lxml import etree
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

contents = pd.DataFrame()
options = Options()
# options.headless = True
options.add_argument("--proxy-server=http://127.0.0.1:1080")
browser = webdriver.Firefox(options=options)
for i in range(1,5):
    url = "https://fs.fang.anjuke.com/loupan/all/a1_p" + str(i) + "_w1/"
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
               'Connection': 'keep-alive',
               'Host':'fs.fang.anjuke.com',
               'Referer':'https://fs.fang.anjuke.com/loupan/all/a1/',
               'Cookie':'ctid=24; aQQ_ajkguid=A8A1CB2C-86F2-F107-F640-SX0418114525; sessid=B03C0B19-41E2-CFA1-E3F2-SX0418114525; isp=true; lps=http%3A%2F%2Fuser.anjuke.com%2Fajax%2FcheckMenu%2F%3Fr%3D0.335350633946187%26callback%3DjQuery1113015611649916074155_1555559128722%26_%3D1555559128723%7Chttps%3A%2F%2Ffs.fang.anjuke.com%2Fxinfang%2F404.html; twe=2; Hm_lvt_c5899c8768ebee272710c9c5f365a6d8=1555559129; Hm_lpvt_c5899c8768ebee272710c9c5f365a6d8=1555559190; 58tj_uuid=a9a8dbf8-07a8-4552-aea3-c5dadf3f6910; new_session=0; init_refer=; new_uv=1; wmda_uuid=f9ebbea80275ab84b2a2cbd4dbad5e94; wmda_new_uuid=1; wmda_session_id_8788302075828=1555559129383-8f780eb2-0a86-323f; wmda_visited_projects=%3B8788302075828; als=0; isp=true; __xsptplusUT_8=1; __xsptplus8=8.1.1555559181.1555559188.2%234%7C%7C%7C%7C%7C%23%23xUxYcRHAs2NXHA4psAvBY_txo39vZ3er%23',
               'Upgrade-Insecure-Requests': '1',
               'TE': 'Trailers',
               'Pragma': 'no-cache',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    proxy = {"https": "http://127.0.0.1:1080"}
    page_info = requests.get(url,proxies=proxy, headers=headers).text

    # print(page_info)
    dom = etree.HTML(page_info)

    links_xpath = dom.xpath("//div[@class='item-mod ']")
    links = ["https://m.anjuke.com/fs/loupan/" + x.attrib['data-link'][-11:-5] + "/params/" for x in links_xpath]
    dictionary = {}

    for link in links:
        browser.get(url=link)
        try:
            dictionary['name'] = browser.find_element_by_xpath("//h3[@class='lp_name']").text
        except Exception as e:
            print(e)
            break
        features = browser.find_elements_by_xpath("//li[@class='ptese']/a")
        dictionary['feature'] = [x.text for x in features]
        labels_xpath = browser.find_elements_by_xpath("//li[@class='info']/label")
        labels = [x.text for x in labels_xpath]
        values_xpath = browser.find_elements_by_xpath("//li[@class='info']/span")
        values = [x.text for x in values_xpath]
        for k, label in enumerate(labels):
            dictionary[label[:-1]] = values[k]

        result = pd.Series(dictionary)
        contents = contents.append(other=result, ignore_index=True)

contents = contents.drop(columns=['预售证号','发证时间','绑定楼栋'])
contents['在售户型'] = contents['在售户型'].map(lambda x: x[:-8])
df_name = contents['name']
contents = contents.drop(columns='name')
contents.insert(0, 'id', df_name)
contents.to_excel("fs_anjuke.xlsx")
contents.to_csv("fs_anjuke.csv")