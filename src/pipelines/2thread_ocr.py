# -*- coding: utf-8 -*-

import base64
import json
import os
import shutil
import threading
import time
import traceback
from datetime import datetime

from pathlib import Path
import PIL
import numpy as np
import requests
from PIL import Image
from tqdm import tqdm
from src.common.fileutils import *
from src.common.errors import OCRFatalError


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


def compress_image_wh2(infile, outfile, _width=None,      _height=None,     isratio=True,     max_size_mb=10, scale_ratio=0.9):
    """
    将超过指定大小的图片循环缩小，直到文件大小不超过 max_size_mb。

    :param infile: 输入图片路径
    :param outfile: 输出图片路径
    :param _width: 兼容旧调用，当前不使用
    :param _height: 兼容旧调用，当前不使用
    :param isratio: 兼容旧调用，当前不使用
    :param max_size_mb: 最大文件大小，默认 10 MB
    :param scale_ratio: 每轮宽高缩放比例，默认 0.9
    :return: 输出图片大小，单位 KB
    """
    Image.MAX_IMAGE_PIXELS = 2300000000

    infile = Path(infile)
    outfile = Path(outfile)

    if not infile.exists():
        raise FileNotFoundError(f"输入图片不存在：{infile}")

    if not 0 < scale_ratio < 1:
        raise ValueError("scale_ratio 必须大于 0 且小于 1")

    outfile.parent.mkdir(parents=True, exist_ok=True)

    max_size_bytes = max_size_mb * 1024 * 1024
    source_size = infile.stat().st_size

    # 未超过10MB，不进行压缩
    if source_size <= max_size_bytes:
        if infile.resolve() != outfile.resolve():
            shutil.copy2(infile, outfile)

        return round(source_size / 1024, 2)

    with Image.open(infile) as source_image:
        # 避免部分图片使用懒加载，关闭源文件后数据不可用
        source_image.load()

        # 保留原图，用累计比例从原图缩放，避免反复缩放造成额外画质损失
        original_image = source_image.copy()
        original_width, original_height = original_image.size
        cumulative_ratio = 1.0

        # JPEG不支持透明通道
        output_suffix = outfile.suffix.lower()
        if output_suffix in {".jpg", ".jpeg"}:
            if original_image.mode != "RGB":
                original_image = original_image.convert("RGB")

        while True:
            cumulative_ratio *= scale_ratio

            new_width = max(1, int(original_width * cumulative_ratio))
            new_height = max(1, int(original_height * cumulative_ratio))

            resized_image = original_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )

            save_kwargs = {}

            # JPEG可加入常用保存参数
            if output_suffix in {".jpg", ".jpeg"}:
                save_kwargs = {
                    "quality": 95,
                    "optimize": True
                }
            elif output_suffix == ".png":
                save_kwargs = {
                    "optimize": True
                }

            resized_image.save(outfile, **save_kwargs)
            resized_image.close()

            current_size = outfile.stat().st_size

            # 当前输出文件已经小于等于10MB
            if current_size <= max_size_bytes:
                break

            # 防止图片已经缩小到极限后陷入死循环
            if new_width == 1 and new_height == 1:
                raise RuntimeError(
                    f"图片已缩小至 1×1，但文件仍超过 {max_size_mb}MB"
                )

    return round(outfile.stat().st_size / 1024, 2)



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

        for file_path in tqdm(jpglist,desc=os.path.basename(bookdir)):
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
                compress_image_wh2(file_path, topath, 300, 1000, True)
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
                else:
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
    booklist = os.listdir(src)
    _idx = 0
    for idx, name in enumerate(booklist):
        bookdir = os.path.join(src, name)
        if not os.path.isdir(bookdir):
            continue
        json_dir = os.path.join(bookdir, 'json')
        page_dir = os.path.join(bookdir, 'pageimages_old')
        pagelist = traverse_dir(page_dir,[],['.jpg'])
        if os.path.isdir(json_dir) and os.path.isdir(page_dir):
            if len(os.listdir(json_dir)) == len(pagelist):
                print(f'已完成第{_idx+1}本 {name}，共{len(booklist)}本')
                _idx += 1
                continue

        bookdirlist.append(bookdir)
        # _idx += 1
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
