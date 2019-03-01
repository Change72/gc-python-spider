import os
import csv
import time
import random
import win32gui
import win32con
from selenium import webdriver


PATH = os.getcwd() + '\\video\\'


def files_in_folder():
    filelist = os.listdir(PATH)          #该文件夹下所有的文件（包括文件夹）
    full_list = []
    name_list = []
    for file in filelist:
        full_list.append(PATH + file)               # 获取 路径 + 文件名+后缀，用于上传
        name_list.append(os.path.splitext(file)[0]) # 只获取文件名，用于excel标识
    return [full_list, name_list]


def random_filename_string(filelist, top):
    string = ""
    length = random.randint(10, 20)

    if top + length > len(filelist):
        length = len(filelist) - top
    for i in range(length):
        string = string + "\"" + filelist[top + i] + "\" "

    bottom = top + length
    return [string, bottom]


def write_csv(data):
    filename = "translation.csv"
    f = open(filename, 'a', newline='', encoding='utf-8')
    Writer = csv.writer(f)
    Writer.writerow(data)
    f.close()
    return

def Spider(url, index, filelist, filename):
    browser = webdriver.Firefox()
    browser.get(url)
    browser.maximize_window()
    browser.implicitly_wait(4)

    browser.find_element_by_id("picker").click()
    browser.find_element_by_id("picker").click()
    browser.find_element_by_id("picker").click()

    time.sleep(random.uniform(1, 2))
    # win32gui
    dialog = win32gui.FindWindow('#32770', '文件上传')  # 对话框
    ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None)
    ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
    Edit = win32gui.FindWindowEx(ComboBox, 0, 'Edit', None)  # 上面三句依次寻找对象，直到找到输入框Edit对象的句柄
    button = win32gui.FindWindowEx(dialog, 0, 'Button', None)  # 确定按钮Button

    win32gui.SendMessage(Edit, win32con.WM_SETTEXT, None, filename)  # 往输入框输入绝对地址
    win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)  # 按button

    time.sleep(random.uniform(8, 20))
    browser.find_element_by_id("en_order").click()

    # browser.find_element_by_class_name("one_btn").click()
    for btn in browser.find_elements_by_class_name("one_btn"):
        time.sleep(random.uniform(0, 1))
        btn.click()
        time.sleep(random.uniform(8, 13))
        write_csv([filelist[index], browser.find_element_by_id("one_div").text])
        browser.find_element_by_xpath('//div/img[@onclick="closeOne()"]').click()
        index = index + 1

    browser.implicitly_wait(5)
    browser.quit()


if __name__ == '__main__':
    url = "https://www.iflyrec.com/html/addMachineOrder.html"
    [full_list, name_list] = files_in_folder()
    top = 0
    while top < len(full_list):
        [filename, bottom] = random_filename_string(full_list, top)
        Spider(url, top, name_list, filename)
        top = bottom
