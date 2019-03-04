import time
import json
from selenium import webdriver

url = "https://mail.126.com/"


def get_cookie():
    browser = webdriver.Firefox()
    browser.get(url)
    browser.maximize_window()
    browser.implicitly_wait(5)
    time.sleep(15)
    # 此处需要手动填写用户名密码等信息进行登陆，记录下登陆的cookie
    cookie = browser.get_cookies()
    print(cookie)
    with open('cookie.txt', 'w') as file:
        file.write(json.dumps(cookie))
        file.close()
    browser.quit()


def load_cookie():
    browser = webdriver.Firefox()
    # 先 get(url) 再添加 cookie
    browser.get(url)
    time.sleep(5)
    with open('cookie.txt', 'r') as file:
        cookie = file.read()
        cookie = json.loads(cookie)
        file.close()
    for i in range(len(cookie)):
        browser.add_cookie(cookie[i])

    # 刷新页面
    browser.get(url)
    browser.maximize_window()
    browser.implicitly_wait(5)
    time.sleep(2)

if __name__ == '__main__':
    get_cookie()
    time.sleep(5)
    load_cookie()
