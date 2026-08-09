# -*- coding: utf-8 -*-

import base64
import json
import os
import threading
import time
import traceback
from datetime import datetime

import PIL
import numpy as np
import requests
from PIL import Image
from tqdm import tqdm
from common.fileutils import *
from common.errors import OCRFatalError


def compress_image_wh(infile, outfile, _width, _height, isratio):
    Image.MAX_IMAGE_PIXELS = 2300000000
    #print("==>压缩到固定高宽 ", _height, "->", _width)

    with  Image.open(infile) as my_image:

        #print("The original size is: ", round(len(my_image.fp.read())/1024,2), "KB")
        #Image.NEAREST ：低质量 
        #Image.BILINEAR：双线性 
        #Image.BICUBIC ：三次样条插值 
        #Image.ANTIALIAS：高质量
        #compressed the image
        if isratio is not True:
            my_image = my_image.resize((int(_width), int(_height)), PIL.Image.LANCZOS)

        else:
            # the original width and height of the image
            image_height = my_image.height
            image_width = my_image.width

            radio = image_height / image_width
            width = _height / radio
            width_radio = int(width)
            #print("==>计算后的宽度：", width_radio)
            my_image = my_image.resize((int(width_radio), int(_height)), PIL.Image.LANCZOS)
            #my_image = my_image.resize((int(image_width / 2), int(image_height / 2)),PIL.Image.LANCZOS)

        my_image = my_image.convert("RGB")
        #save the image
        my_image.save(outfile)

        #open the compressed image
        picsize = 0
        with Image.open(outfile) as compresed_image:
            picsize = round(len(compresed_image.fp.read()) / 1024, 2)
            #print("The size of compressed image is: ", picsize, 'kb')
            #print("topath=",topath)
            return picsize


def ocrbook(bookdirlist, threadID, url, error_file_path, stop_event, errors):
    booklistbar = tqdm(bookdirlist)
    for bookdir in booklistbar:
        if stop_event.is_set():
            return
        jsondirpath = os.path.join(bookdir, "json")
        booklistbar.set_description("解析图书 %s" % bookdir)
        os.makedirs(jsondirpath, exist_ok=True)

        jpglist = traverse_dir(os.path.join(bookdir, "pageimages_old"), [], ['.jpg'])
        newpicdirpath = os.path.join(bookdir, "pageimages")
        os.makedirs(newpicdirpath, exist_ok=True)

        for file_path in tqdm(jpglist):
            if stop_event.is_set():
                return
            fname = os.path.basename(file_path)
            basename, _ = os.path.splitext(fname)
            topath = os.path.join(newpicdirpath, fname)
            jsonpath = os.path.join(jsondirpath, basename + ".json")
            if os.path.exists(jsonpath):
                continue
            try:
                compress_image_wh(file_path, topath, 300, 1000, True)
                with open(topath, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                payload = json.dumps({
                    'image': image_base64,
                    'imgName': fname,
                    'layout': 'single_column',
                })
                response = requests.post(url=url, data=payload, timeout=7200)
                response.raise_for_status()
                json_data = response.json()
                if json_data.get('code') != 200:
                    append_txt("null", jsonpath)
                with open(jsonpath, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False)
            except Exception as exc:
                append_txt("path=" + file_path, error_file_path)
                errors.append((file_path, exc))
                stop_event.set()
                return


def ocrbook1(bookdirlist, threadID):
    #print(bookdirlist)  
    booklistbar = tqdm(bookdirlist)
    for bookdir in booklistbar:
        print("==>线程-", threadID, ":", bookdir)
        booklistbar.set_description("解析图书 %s" % bookdir)


class myThread(threading.Thread):
    def __init__(self, bookdirlist, threadID, url, error_file_path, stop_event, errors):
        super().__init__(name=f"ocr-thread-{threadID}")
        self.bookdirlist = bookdirlist
        self.threadID = threadID
        self.url = url
        self.error_file_path = error_file_path
        self.stop_event = stop_event
        self.errors = errors

    def run(self):
        ocrbook(
            self.bookdirlist,
            self.threadID,
            self.url,
            self.error_file_path,
            self.stop_event,
            self.errors,
        )


#import numpy as np


def scanbook(src, url, error_file_path):
    if not url:
        raise OCRFatalError("OCR接口地址为空")
    if os.path.exists(error_file_path):
        os.remove(error_file_path)

    bookdirlist = []
    for name in os.listdir(src):
        bookdir = os.path.join(src, name)
        if not os.path.isdir(bookdir):
            continue
        json_dir = os.path.join(bookdir, 'json')
        page_dir = os.path.join(bookdir, 'pageimages_old')
        if os.path.isdir(json_dir) and os.path.isdir(page_dir):
            if len(os.listdir(json_dir)) == len(os.listdir(page_dir)):
                continue
        bookdirlist.append(bookdir)

    if not bookdirlist:
        print("没有需要识别的图书")
        return

    threadcount = min(3, len(bookdirlist))
    groups = np.array_split(bookdirlist, threadcount)
    stop_event = threading.Event()
    errors = []
    threads = [
        myThread(group.tolist(), idx + 1, url, error_file_path, stop_event, errors)
        for idx, group in enumerate(groups)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    if errors:
        file_path, exc = errors[0]
        raise OCRFatalError(f"OCR识别失败：{file_path}；{exc}") from exc

    print("==>全部处理完毕<==")
