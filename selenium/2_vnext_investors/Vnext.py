import re
import os
import csv
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def write_csv(data):
    filename = "Investors_Info.csv"
    f = open(filename, 'a', newline='', encoding='utf-8')
    Writer = csv.writer(f)
    Writer.writerow(data)
    f.close()
    return


def Spider(url):
    browser = webdriver.Firefox()
    browser.get(url)
    browser.maximize_window()
    browser.implicitly_wait(5)

    username = "*********"
    password = "*********"
    browser.find_element_by_id("name").send_keys(username)
    browser.find_element_by_id("pwd").send_keys(password)
    browser.find_element_by_id("pwd").send_keys(Keys.ENTER)
    browser.implicitly_wait(5)

    write_csv(["Seq", "Name", "Institution", "Position", "Location", "Investment_Areas", "Experience",
               "Investment_Case", "Investment_Regions", "Investment_Stage", "Investment_Amount", "Email_Details"])
    detail_url = "https://www.v-next.cn/sizeInvtpersn/detail.do?id="
    for i in range(2, 128):

        name = "-"
        institution = "-"
        position = "-"
        location = "-"
        investment_Areas = "-"
        experience = "-"
        investment_Case = "-"
        investment_Regions = "-"
        investment_Stage = "-"
        investment_Amount = "-"
        email_Details = "-"

        new_url = detail_url + str(i)
        browser.get(new_url)
        # head
        try:
            name = browser.find_element_by_xpath("//div[@class='invt_dt_ct_tzr_text pull-left']/h4").text
        except Exception as e:
            continue

        try:
            title = browser.find_elements_by_xpath("//div[@class='invt_dt_ct_tzr_text pull-left']/p")
            [institution, position, location] = [row.text for row in title]
        except Exception as e:
            pass

        # body
        try:
            body_keys = browser.find_elements_by_xpath("//div[@class='invt_dt_ct_bd_info']/h4")
            body_values = browser.find_elements_by_xpath("//div[@class='invt_dt_ct_bd_info']/p")
            final_keys = [row.text for row in body_keys]
            final_values = [row.text for row in body_values]
            dictionary = dict(zip(final_keys, final_values))
        except Exception as e:
            dictionary = {}

        if "Investment Areas" in dictionary.keys():
            investment_Areas = dictionary["Investment Areas"]
        if "Experience" in dictionary.keys():
            experience = dictionary["Experience"]
        if "Investment Case" in dictionary.keys():
            investment_Case = dictionary["Investment Case"]
        if "Inverstment Regions" in dictionary.keys():
            investment_Regions = dictionary["Inverstment Regions"]

        # stage
        try:
            stage = browser.find_element_by_xpath("//div[@class='invt_dt_stage']").text
            investment_Stage = stage
            while investment_Stage.find("\n") != -1:
                investment_Stage = investment_Stage.replace("\n", "、")
        except Exception as e:
            pass

        # amount
        try:
            amount = browser.find_element_by_xpath("//div[@class='invt_dt_money']").text
            investment_Amount = amount
        except Exception as e:
            pass

        # email
        try:
            email = browser.find_element_by_xpath("//div[@class='invt_dt_ct_bd_right']/a").text
            email_Details = email
        except Exception as e:
            pass

        write_csv([i, name, institution, position, location, investment_Areas, experience, investment_Case,
                   investment_Regions, investment_Stage, investment_Amount, email_Details])

        try:
            img = browser.find_element_by_xpath("//div[@class='invt_dt_ct_hd_img pull-left']").get_attribute("style")
            pattern = re.compile(u'\("(.*\.jpg)"\)')
            img = pattern.findall(img)
            img_name = str(i) + "_" + name
            img_url = "https://www.v-next.cn" + str(img[0])

            path = str(os.getcwd()) + "\image\\"
            with open((path +  str(img_name) + ".jpg"), 'wb') as f:
                f.write(urllib.request.urlopen(img_url).read())
                f.close()
        except Exception as e:
            pass


if __name__ == '__main__':
    url = "https://www.v-next.cn/log/login.do"
    Spider(url)
