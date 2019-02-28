from PIL import Image
import os
origin_files_path= "image"

def reduce_size():
    reduce_path = origin_files_path + "_reduce_size"
    if not os.path.exists(reduce_path):
        os.mkdir(reduce_path)

    filelist = os.listdir(origin_files_path)
    for file in filelist:
        image = Image.open(origin_files_path + "\\" + file)
        width, height = image.size
        target_height = 100 * height / width
        image = image.resize((100, int(target_height)), Image.ANTIALIAS)
        image.save(reduce_path + "\\" + file, optimize=True, quality=95)

reduce_size()