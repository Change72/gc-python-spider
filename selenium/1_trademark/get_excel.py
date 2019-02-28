import os
import csv
import time
import xlsxwriter
from PIL import Image

# 此版本不带默认 csv 带表头

keyword = "财新传媒有限公司"
origin_files_path= "image"

def get_filename():
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    return keyword + "_" + date


def get_trademark_info():
    trademark_info_dict = {}
    csvReader = csv.reader(open(get_filename() + ".csv", 'r', encoding='utf-8'))
    for row in csvReader:
        trademark_info_dict[row[0]] = row[1:(len(row) - 1)]
    return trademark_info_dict


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


def write_line(worksheet):
    # format
    context = workbook.add_format()
    context.set_font_size(9)
    context.set_align("center")
    context.set_align("vcenter")
    context.set_text_wrap()

    dict = get_trademark_info()
    print(len(dict))
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
    workbook = xlsxwriter.Workbook(get_filename() + ".xlsx")
    worksheet = workbook.add_worksheet()

    reduce_size()

    write_title(worksheet)
    write_line(worksheet)

    workbook.close()