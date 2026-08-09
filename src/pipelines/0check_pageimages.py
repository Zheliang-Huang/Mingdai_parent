import os

from tqdm import tqdm
from common.config import *
from common.excel_utils import *
from common.fileutils import *


def check_if_miss(check1, check2, check3):
    if check1 is True or check2 is True or check3 is True:
        res_list = ['否', '否', '否']
        if check1:
            res_list[0] = '是'
        if check2:
            res_list[1] = '是'
        if check3:
            res_list[2] = '是'
        return res_list


def run(src: str, tifs: str, output: str):
    source = src
    tif_path = tifs
    result_file = output
    book_dics = {}
    for book in tqdm(os.listdir(source), desc='彩图读取'):
        book_path = os.path.join(source, book)
        if os.path.isdir(book_path):
            pic_dirs = []
            traverse_dir(book_path, pic_dirs, ['.jpg', '.jpeg', '.tif'])
            book_dics[book] = pic_dirs
    excel_list = []
    for book in tqdm(os.listdir(tif_path), desc='黑白图读取'):
        zsknum = book.split(' ')[0]
        if book not in book_dics:
            continue
        book_path = os.path.join(tif_path, book)
        if os.path.isdir(book_path):
            tif_pic_list = []
            traverse_dir(book_path, tif_pic_list, ['.tif', '.tiff'])
            tif_list = [os.path.splitext(os.path.basename(tif_file))[
                            0] for tif_file in tif_pic_list]
            jpg_list = book_dics[book]
            for jpg_file in jpg_list:
                if_miss_part = False
                zsk_wrong = False
                different_name = False
                basename = os.path.splitext(os.path.basename(jpg_file))[0]
                name_split = basename.split('-')
                if len(name_split) == 2:
                    if_miss_part = True
                picnum = name_split[0]
                if picnum != zsknum:
                    zsk_wrong = True
                if basename not in tif_list:
                    different_name = True

                check_bools = check_if_miss(
                    if_miss_part, zsk_wrong, different_name)
                if check_bools:
                    excel_list.append(
                        [zsknum, basename, check_bools[0], check_bools[1], check_bools[2]])
    create_excel(['著录号', '图片名', '是否缺少字段', '著录号是否正确',
                  '是否与黑白图不一致'], excel_list, result_file)
