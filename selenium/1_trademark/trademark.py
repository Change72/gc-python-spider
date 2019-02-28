import csv
import re
import os
import time
import random
import shutil
import requests
import operator
import xlsxwriter
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains


keyword = "财新传媒有限公司"
origin_files_path= "image"
dict = {}


def get_filename():
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    return keyword + "_" + date


def write_csv(data):
    filename = get_filename()
    f = open(filename + ".csv", 'a', newline='', encoding='utf-8')
    Writer = csv.writer(f)
    Writer.writerow(data)
    f.close()
    return


def write_img(i, img):
    f = open("img_url.csv", 'a', newline='', encoding='utf-8')
    Writer = csv.writer(f)
    Writer.writerow([i, img])
    f.close()
    return


def scan_done():
    filelist = os.listdir(origin_files_path)
    already_done = []
    for files in filelist:                          #遍历所有文件
        num = os.path.splitext(files)[0]            #文件名
        already_done.append(int(num))
    return already_done


def remove_done(totalList):
    already_done = scan_done()
    for i in already_done:
        totalList.remove(i - 1)
    print(len(totalList))
    return totalList


def get_img(filename, img):
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    with open((origin_files_path + "\\" + filename + ".jpg"), 'wb') as f:
        r = requests.get(img, headers=headers)
        f.write(r.content)
        f.close()


def replace_enter(target):
    while target.find("\\n") != -1:
        target = target.replace("\\n", " ")
    return target


def open_browser(url, keyword):
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    browser.implicitly_wait(5)
    browser.get(url)
    browser.maximize_window()

    time.sleep(random.uniform(5, 10))
    temp = browser.find_element_by_id("txnS02")
    ActionChains(browser).move_to_element(temp).click().perform()
    time.sleep(random.uniform(5, 8))

    blank = browser.find_element_by_name("request:hnc")
    blank.send_keys(keyword)
    time.sleep(random.uniform(3, 5))
    target = browser.find_element_by_id("_searchButton")
    ActionChains(browser).move_to_element_with_offset(target, 0, 20).click().perform()
    browser.implicitly_wait(20)
    time.sleep(random.uniform(30, 35))
    handles = browser.window_handles
    browser.switch_to.window(handles[1])
    return browser


def scan_info(i, browser):
    # declare
    info_product = ""  # 商品/服务
    info_product_code = ""  # 商品编号
    info_code = ""  # 申请/注册号
    info_application_date = ""  # 申请日期
    info_global_classify = 0  # 国际分类
    info_applicant_cn = ""  # 申请人名称（中文）
    info_applicant_en = ""  # 申请人名称（英文）
    info_apply_address_cn = ""  # 申请人地址（中文）
    info_apply_address_en = ""  # 申请人地址（英文）
    info_announcement_first_code = ""  # 初审公告期号
    info_announcement_signup_code = ""  # 注册公告期号
    info_is_share_trademark = ""  # 是否共有商标
    info_announcement_first_date = ""  # 初审公告日期
    info_announcement_signup_date = ""  # 注册公告日期
    info_trademark_type = ""  # 商标类型
    info_right_term = ""  # 专用权期限
    info_trademark_form = ""  # 商标形式
    info_global_signup_date = ""  # 国际注册日期
    info_late_date = ""  # 后期指定日期
    info_priority_date = ""  # 优先权日期
    info_agency = ""  # 代理/办理机构
    info_trademark_status_details = ""  # 商标状态详情（因商标状态栏随机出现，此处匹配最后一个）

    # getInfo
    i = i + 1
    try:
        info = browser.find_elements_by_xpath("//td[@class='info']")

        # info_product = ""  # 商品/服务
        info_product = replace_enter(info[0].text)

        # info_product_code = ""  # 商品编号
        info_product_code = info[1].text

        # info_code = ""  # 申请/注册号
        info_code = info[2].text
        if str(i) in dict.keys():
            if not operator.eq(info_code, dict[str(i)]):
                return False
        else:
            return False

        # info_application_date = ""  # 申请日期
        info_application_date = info[3].text

        # info_global_classify = 0  # 国际分类
        info_global_classify = info[4].text

        # info_applicant_cn = ""  # 申请人名称（中文）
        info_applicant_cn = info[5].text

        # info_applicant_en = ""  # 申请人名称（英文）
        info_applicant_en = info[6].text

        # info_apply_address_cn = ""  # 申请人地址（中文）
        info_apply_address_cn = info[7].text

        # info_apply_address_en = ""  # 申请人地址（英文）
        info_apply_address_en = info[8].text

        # info_announcement_first_code = ""  # 初审公告期号
        info_announcement_first_code = info[9].text

        # info_announcement_signup_code = ""  # 注册公告期号
        info_announcement_signup_code = info[10].text

        # info_is_share_trademark = ""  # 是否共有商标
        info_is_share_trademark = replace_enter(info[11].text)

        # info_announcement_first_date = ""  # 初审公告日期
        info_announcement_first_date = info[12].text

        # info_announcement_signup_date = ""  # 注册公告日期
        info_announcement_signup_date = info[13].text

        # info_trademark_type = ""  # 商标类型
        info_trademark_type = info[14].text

        # info_right_term = ""  # 专用权期限
        info_right_term = replace_enter(info[15].text)

        # info_trademark_form = ""  # 商标形式
        info_trademark_form = replace_enter(info[16].text)

        # info_global_signup_date = ""  # 国际注册日期
        info_global_signup_date = info[17].text

        # info_late_date = ""  # 后期指定日期
        info_late_date = info[18].text

        # info_priority_date = ""  # 优先权日期
        info_priority_date = replace_enter(info[19].text)

        # info_agency = ""  # 代理/办理机构
        info_agency = info[20].text

        # info_trademark_status_details = ""  # 商标状态详情（因商标状态栏随机出现，此处匹配最后一个）
        info_trademark_status_details = replace_enter(info[len(info) - 1].text)
        pattern = u"[\u4E00-\u9FA5]+"
        info_trademark_status_details = re.compile(pattern).search(info_trademark_status_details).group()

    except Exception as e:
        print(e)
        return False

    # write_csv(["编号", "商品/服务", "申请/注册号", "申请日期", "国际分类", "申请人名称（中文）", "初审公告日期",
    #            "注册公告日期", "专用权期限", "代理/办理机构", "商标状态详情", "商品编号", "申请人名称（英文）",
    #            "申请人地址（中文）", "申请人地址（英文）", "初审公告期号", "注册公告期号", "是否共有商标", "商标类型", "商标形式",
    #            "商标形式", "国际注册日期", "后期指定日期", "优先权日期"])

    write_csv([i, info_product, info_code, info_application_date, info_global_classify, info_applicant_cn,
               info_announcement_first_date, info_announcement_signup_date, info_right_term, info_agency,
               info_trademark_status_details, info_product_code, info_applicant_en, info_apply_address_cn,
               info_apply_address_en, info_announcement_first_code, info_announcement_signup_code,
               info_is_share_trademark, info_trademark_type, info_trademark_form, info_global_signup_date,
               info_late_date, info_priority_date])

    time.sleep(random.uniform(2, 5))
    try:
        img = browser.find_element_by_xpath("//img[@id='tmImage']").get_attribute("src")
        print(str(i), img)
        write_img(str(i), img)
        get_img(str(i), img)
    except Exception as e:
        print(e)
        return False

    return True


def put_index(browser):
    rows = browser.find_elements_by_xpath("//tr[@class='ng-scope']/td")     #300个，1为标签，2为注册号
    i = 0
    num = ""
    code = ""
    for row in rows:
        i = i + 1
        if i % 6 == 1:
            num = row.text
        elif i % 6 == 2:
            code = row.text
            if num not in dict.keys():
                dict[num] = code
        else:
            continue
    print(dict)


def Spider(url, keyword):
    flag = False
    while True:
        try:
            if not flag:
                browser = open_browser(url, keyword)
            put_index(browser)
            totalNum = browser.find_element_by_xpath("//strong[@class='totalnumber ng-binding']").text
            break
        except Exception as e:
            print(e)
            if not flag:
                flag = True
                handles = browser.window_handles
                browser.switch_to.window(handles[0])
                blank = browser.find_element_by_name("request:hnc")
                blank.send_keys(" ")
                time.sleep(random.uniform(3, 5))
                target = browser.find_element_by_id("_searchButton")
                ActionChains(browser).move_to_element_with_offset(target, 0, 20).click().perform()
                browser.implicitly_wait(20)
                time.sleep(random.uniform(30, 35))
                handles = browser.window_handles
                browser.switch_to.window(handles[1])
            else:
                browser.quit()
                time.sleep(60)
                flag = False
            continue

    print(totalNum)
    totalList = list(range(int(totalNum)))
    totalList = remove_done(totalList)
    print(totalList)

    random.shuffle(totalList)
    each_num = 0
    if len(totalList) > 50:
        each_num = 50
    else:
        each_num = len(totalList) / 2 + 1
    while len(totalList) > 0:
        if len(totalList) > each_num:
            one_time = totalList[0:int(each_num)]
        else:
            one_time = totalList[0:len(totalList)]
        list.sort(one_time)
        print(one_time)
        current_head = 0
        current_location = 0
        for i in one_time:
            while i - current_head > 49:
                # next page
                current_head = current_head + 50
                current_location = 0
                browser.find_element_by_css_selector("body").click()
                browser.find_element_by_css_selector("body").send_keys(Keys.END)
                time.sleep(random.uniform(2, 4))
                try:
                    nextPageButtom = browser.find_element_by_xpath("//li[@class='nextPage']/a")
                    ActionChains(browser).move_to_element(nextPageButtom).click().perform()
                    browser.implicitly_wait(10)
                    time.sleep(random.uniform(5, 10))
                except Exception as e:
                    print(e)
                    browser.quit()
                    browser = open_browser(url, keyword)
                    current_head = 0
                    current_location = 0
                    one_time.append(i)
                    continue

                browser.find_element_by_css_selector("body").click()
                browser.find_element_by_css_selector("body").send_keys(Keys.HOME)
                browser.implicitly_wait(10)
                time.sleep(random.uniform(5, 10))
                put_index(browser)
            while i - current_head - current_location > 21:
                # page down
                current_location = current_location + 22
                browser.find_element_by_css_selector("body").click()
                browser.find_element_by_css_selector("body").send_keys(Keys.PAGE_DOWN)
                browser.implicitly_wait(10)
                time.sleep(random.uniform(1, 3))

            try:
                # enter and get info
                details = browser.find_elements_by_xpath("//a[@class='ng-binding']")
                ActionChains(browser).move_to_element(details[2 * (i - current_head)]).click().perform()
                browser.implicitly_wait(2)
                time.sleep(random.uniform(5, 10))
                all_handles = browser.window_handles
                browser.switch_to.window(all_handles[2])
                browser.implicitly_wait(2)
                time.sleep(random.uniform(10, 15))

                if scan_info(i, browser):
                    totalList.remove(i)
                time.sleep(random.uniform(2, 5))

            except Exception as e:
                print(e)
                pass

            # switch back
            all_handles = browser.window_handles
            browser.switch_to.window(all_handles[1])
            browser.implicitly_wait(2)
            time.sleep(random.uniform(5, 10))

        browser.find_element_by_css_selector("body").click()
        browser.find_element_by_css_selector("body").send_keys(Keys.END)
        browser.implicitly_wait(5)
        time.sleep(random.uniform(2, 5))
        if one_time[len(one_time) - 1] > 49:
            first_page = browser.find_element_by_xpath("//li[@class='firstPage']/a")
            ActionChains(browser).move_to_element(first_page).click().perform()
            browser.implicitly_wait(10)
            time.sleep(random.uniform(5, 10))
        browser.find_element_by_css_selector("body").click()
        browser.find_element_by_css_selector("body").send_keys(Keys.HOME)
        browser.implicitly_wait(10)
        time.sleep(random.uniform(5, 10))

    browser.quit()


def copy_files():
    copy_path = origin_files_path + "_copy"
    if not os.path.exists(copy_path):
        shutil.copytree(origin_files_path, copy_path)


def get_img_url():
    img_dict = {}
    csvReader = csv.reader(open("img_url.csv", 'r'))
    for row in csvReader:
        img_dict[row[0]] = row[1]
    return img_dict


def re_get_imgs():
    filelist = os.listdir(origin_files_path)
    img_dict = get_img_url()
    is_re_get = False
    for file in filelist:                   #遍历所有文件
        file_path = origin_files_path + "\\" + file
        if int(os.path.getsize(file_path)) < 2048:
            is_re_get = True
            filename = os.path.splitext(file)[0]  # 文件名
            if filename in img_dict.keys():
                img_url = img_dict[filename]
                os.remove(file_path)
                get_img(filename, img_url)
            else:
                print(filename + "is not in the dictionary")
    return is_re_get


def get_trademark_info():
    trademark_info_dict = {}
    csvReader = csv.reader(open(get_filename() + ".csv", 'r', encoding='utf-8'))
    for row in csvReader:
        trademark_info_dict[row[0]] = row[1:(len(row) - 1)]
    return trademark_info_dict


def reduce_size():
    reduce_path = origin_files_path + "_reduce_size"
    if not os.path.exists(reduce_path):
        os.mkdir(reduce_path)

    filelist = os.listdir(origin_files_path)
    for file in filelist:
        image = Image.open(origin_files_path + "\\" + file)
        width, height = image.size
        target_width = 75
        target_height = target_width * height / width
        image = image.resize((target_width, int(target_height)), Image.ANTIALIAS)
        image.save(reduce_path + "\\" + file, optimize=True, quality=95)
    return reduce_path


def write_title(worksheet):
    title = ["编号", "标样", "商品/服务", "注册号", "申请日期", "国际分类", "申请人名称（中文）", "初审公告日期",
                "注册公告日期", "专用权期限", "代理/办理机构", "商标状态详情", "商品编号", "申请人名称（英文）",
                "申请人地址（中文）", "申请人地址（英文）", "初审公告期号", "注册公告期号", "是否共有商标", "商标类型", "商标形式",
                "国际注册日期", "后期指定日期", "优先权日期"]
    col_width = [5, 15, 45, 10, 15, 10, 25, 15, 15, 30, 25, 30, 25, 25, 25, 25, 15, 15, 15, 10, 10, 15, 15, 15]
    print(len(title))
    print(len(col_width))
    title_format = workbook.add_format()
    title_format.set_bold(bold=True)
    title_format.set_font_size(12)
    title_format.set_align("center")
    title_format.set_align("vcenter")
    worksheet.set_row(0, 20, title_format)
    for i, name in enumerate(title):
        worksheet.set_column(i, i, col_width[i])
        worksheet.write(0, i, name)


def write_line(worksheet):
    # format
    context = workbook.add_format()
    context.set_font_size(9)
    context.set_align("center")
    context.set_align("vcenter")
    context.set_text_wrap()

    dict = get_trademark_info()
    for i in range(len(dict)):
        if str(i + 1) in dict.keys():
            worksheet.set_row(i + 1, 60, context)
            infos = dict[str(i + 1)]
            # num
            worksheet.write(i + 1, 0, str(i + 1))
            # pic
            reduced_path = reduce_size()
            pic_path = reduced_path + "//" + str(i + 1) + ".jpg"
            worksheet.insert_image(i + 1, 1, pic_path, {'x_offset': 20, 'y_offset': 2})

            # info
            for k, info in enumerate(infos):
                # if k == 14:
                #     worksheet.write(i + 1, 11, info)
                #     continue
                worksheet.write(i + 1, k + 2, info)




if __name__ == '__main__':
    url = "http://wsjs.saic.gov.cn"
    if not os.path.exists(origin_files_path):
        os.mkdir(origin_files_path)
    print(get_filename())
    Spider(url, keyword)
    copy_files()
    while re_get_imgs():
        continue

    reduce_size()
    workbook = xlsxwriter.Workbook(get_filename() + ".xlsx")
    worksheet = workbook.add_worksheet()

    write_title(worksheet)
    write_line(worksheet)

    workbook.close()