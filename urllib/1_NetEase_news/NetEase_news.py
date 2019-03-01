import os
import re
import requests
from lxml import etree


def StringListSave(save_path, filename, slist):
    # 如果不存在目录则创建目录
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    path = save_path+"/"+filename+".txt"
    with open(path, "w+", encoding='utf-8') as fp:
        for s in slist:
            fp.write("%s\t\t%s\n" % (s[0], s[1]))
            # fp.write("%s\t\t%s\n" % (s[0].encode("utf8"), s[1].encode("utf8")))


def New_Page_Info(new_page):
    '''Regex(slowly) or Xpath(fast)'''
    # new_page_Info = re.findall(r'<td class=".*?">.*?<a href="(.*?)\.html".*?>(.*?)</a></td>', new_page, re.S)
    # # new_page_Info = re.findall(r'<td class=".*?">.*?<a href="(.*?)">(.*?)</a></td>', new_page, re.S) # bugs
    # results = []
    # for url, item in new_page_Info:
    #     results.append((item, url+".html"))
    # return results
    dom = etree.HTML(new_page)
    new_items = dom.xpath('//tr/td/a/text()')
    new_urls = dom.xpath('//tr/td/a/@href')
    # 用以检查某一条件是否为True，若该条件为False则会给出一个AssertionError。
    # 用以检查 标题数 与 url 数目是否对应
    assert(len(new_items) == len(new_urls))
    return zip(new_items, new_urls)


def Page_Info(myPage):
    '''Regex'''
    mypage_Info = re.findall(r'<div class="titleBar" id=".*?"><h2>(.*?)</h2><div class="more"><a href="(.*?)">.*?</a></div></div>', myPage, re.S)
    return mypage_Info


def Spider(url):
    i = 0
    print("downloading ", url)
    myPage = requests.get(url).text
    # print(myPage)

    myPageResults = Page_Info(myPage)
    save_path = u"网易新闻抓取"       # str以unicode格式存储, encode 后变成 bytes
    filename = str(i)+"_"+u"新闻排行榜"
    StringListSave(save_path, filename, myPageResults)
    i += 1
    for item, url in myPageResults:
        print("downloading ", url)
        new_page = requests.get(url).text
        # new_page = urllib.request.urlopen(url).read().decode("gbk")
        newPageResults = New_Page_Info(new_page)
        filename = str(i)+"_"+item
        StringListSave(save_path, filename, newPageResults)
        i += 1


if __name__ == '__main__':
    print("start")
    start_url = "http://news.163.com/rank/"
    Spider(start_url)
    print("end")