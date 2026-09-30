# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime
from src.common.fileutils import *
# import cv2 as cv
from tqdm import tqdm




def run(src):

    file_scan_path = src
    createtime=datetime.now().strftime("%Y-%m-%d")
    print(createtime)
    
   
    bookdirs=os.listdir(file_scan_path)
    bookbar = tqdm(bookdirs)
    for _bookdir in bookbar:
        bookdir = os.path.join(file_scan_path, _bookdir)
        
        bookbar.set_description("解析图书 %s" % _bookdir)
        
       
        picdirpath = bookdir+"\\pageimages_old\\"
               
        if os.path.exists(picdirpath) is True:
           
            shutil.rmtree(picdirpath)
            
                 

    print("==>全部处理完毕<==")
    

