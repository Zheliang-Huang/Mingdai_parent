# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime

from PIL import Image
# import cv2 as cv
from tqdm import tqdm

from src.common.fileutils import *


def run(src, out):
    file_scan_path = src
    file_scan_path_to = out
    createtime = datetime.now().strftime("%Y-%m-%d")
    print(createtime)

    if os.path.exists(file_scan_path_to) is False:
        os.mkdir(file_scan_path_to)

    bookdirs = os.listdir(file_scan_path)
    bookbar = tqdm(bookdirs)
    for _bookdir in bookbar:
        #print(bookdir)
        bookdir = os.path.join(file_scan_path, _bookdir)

        bookbar.set_description("解析图书 %s" % _bookdir)

        jpglist = traverse_dir(bookdir, [], ['.jpg', '.tif', '.tiff'])

        tobookdir = os.path.join(file_scan_path_to, _bookdir)

        if os.path.exists(tobookdir) is False:
            os.mkdir(tobookdir)

        picdirpath = tobookdir + "\\pageimages_old\\"

        if os.path.exists(picdirpath) is False:
            os.mkdir(picdirpath)
        else:
            shutil.rmtree(picdirpath)
            os.mkdir(picdirpath)

        #bar = tqdm(jpglist)
        print("==>图片总数量：", len(jpglist))
        for file_path in jpglist:

            #print("图片先压缩处理", file_path)
            fname = os.path.basename(file_path)
            #bar.set_description("Processing %s" % fname)

            fp = os.path.dirname(file_path)
            basename, ext = os.path.splitext(fname)

            newpicpath = picdirpath + fname
            topath = newpicpath
            if os.path.isfile(topath):
                continue

            if ext.lower() in ['.tif','.tiff']:
                #print(basename)
                outfile = bookdir + "\\" + basename + ".jpg"
                #img=cv.imread(file_path,-1)
                #cv.imwrite(outfile,img)
                Image.MAX_IMAGE_PIXELS = 2300000000

                with  Image.open(file_path) as my_image:

                    #print("The original size is: ", round(len(my_image.fp.read())/1024,2), "KB")
                    #Image.NEAREST ：低质量 
                    #Image.BILINEAR：双线性 
                    #Image.BICUBIC ：三次样条插值 
                    #Image.ANTIALIAS：高质量
                    #compressed the image

                    my_image = my_image.convert("RGB")
                    #save the image
                    my_image.save(outfile)
                file_path = outfile
                newpicpath = picdirpath + basename + ".jpg"
                topath = newpicpath

                shutil.copy(file_path, topath)

                os.remove(file_path)
            else:
                shutil.copy(file_path, topath)

    print("==>全部处理完毕<==")
