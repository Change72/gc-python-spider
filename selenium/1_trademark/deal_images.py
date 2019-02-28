import os
import csv
import shutil
import requests


origin_files_path= "image"


def copy_files():
    copy_path = origin_files_path + "_copy"
    if not os.path.exists(copy_path):
        shutil.copytree(origin_files_path, copy_path)


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




copy_files()
while re_get_imgs():
    continue

