import os
from common.fileutils import *


def run(output_dir, json_extract_dir):
    pic_dir = output_dir
    source = json_extract_dir
    json_list = []
    traverse_dir(source, json_list, ['.json'])
    json_names = [os.path.splitext(os.path.basename(jsonpath))[0] for jsonpath in json_list]

    for book in os.listdir(pic_dir):
        print(book)
        book_dir = os.path.join(pic_dir, book)
        if os.path.isdir(book_dir):
            pic_list = []
            traverse_dir(book_dir, pic_list, ['.jpg', '.tif', '.jpeg'])
            for pic in pic_list:
                picname = os.path.splitext(os.path.basename(pic))[0]
                if picname in json_names:
                    new_pic = os.path.join(source, os.path.basename(pic))
                    copy_file(pic, new_pic)
