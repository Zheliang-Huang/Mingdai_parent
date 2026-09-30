# -*- coding: utf-8 -*-

import os

from PIL import Image
from tqdm import tqdm
from src.common.fileutils import *


def run(errorpath):
    source = errorpath
    if not os.path.isfile(source):
        print('无错误图片')
        return
    else:
        pic_list = [pic_file.replace('path=', '')
                    for pic_file in read_txt_list(source, 'utf-8')]
        for pic in tqdm(pic_list):
            image = Image.open(pic)
            image.save(pic)
            print(pic)
