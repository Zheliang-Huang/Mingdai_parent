from typing import Any, Dict, List


def traverse_dir(file_path, path_read, ext) -> List[str]:
    import os
    new_dir = file_path
    if os.path.isfile(file_path):
        if len(ext) == 0:
            path_read.append(file_path)
        ext_dic = {key: 1 for key in ext}
        if (os.path.splitext(file_path)[-1]).lower() in ext_dic:
            filename = os.path.basename(file_path)
            path_read.append(file_path)

    elif os.path.isdir(file_path):
        # dirlist.append(dirpath)
        for s in os.listdir(file_path):
            new_dir = os.path.join(file_path, s)
            traverse_dir(new_dir, path_read, ext)
    return path_read


def append_txt(txtStr, txtpath):
    f = open(txtpath, 'a', encoding="utf-8")
    f.write(txtStr + '\n')
    f.close()


def append_xml_format(xml_str, xml_path, mode):
    xml_format = xml_str.replace('<?xml version="1.0" encoding="utf-8"?>',
                                 '<?xml version="1.0" encoding="utf-8"?>\n').replace(
        '<语料 xmlns="http://shangyuan/shuju_yuliao" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
        '<语料 xmlns="http://shangyuan/shuju_yuliao" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n').replace(
        '</原书页面><段落', '</原书页面>\n<段落').replace('</标题>', '</标题>\n').replace('</段落>', '</段落>\n')

    f = open(xml_path, mode, encoding="UTF-8")
    f.write(xml_format)
    f.close()


def read_txt_list(filepath, encode) -> List[str]:
    # 不要把open放在try中，以防止打开失败，那么就不用关闭了
    file_object = open(filepath, "r", encoding=encode, errors='ignore')
    try:
        # file_context是一个string，读取完后，就失去了对test.txt的文件引用
        file_context = file_object.readlines()
        datalist = []
        for lineStr in file_context:
            line = lineStr.strip('\n')
            datalist.append(line)
        return datalist
    finally:
        file_object.close()


# 将文件读取成一个完整的字符串
def read_txt_file(filepath, encode) -> str:
    # 不要把open放在try中，以防止打开失败，那么就不用关闭了
    file_object = open(filepath, "r", encoding=encode, errors='ignore')
    try:
        # file_context是一个string，读取完后，就失去了对test.txt的文件引用
        file_context = file_object.readlines()
        xmlstr = ""
        for lineStr in file_context:
            # datalist.append(lineStr)
            xmlstr = xmlstr + lineStr
        return xmlstr
    finally:
        file_object.close()


def read_big_file(filepath) -> str:
    # 不要把open放在try中，以防止打开失败，那么就不用关闭了
    from tqdm import tqdm
    print('正在打开')
    file_object = open(filepath, "rb")
    try:
        # file_context是一个string，读取完后，就失去了对test.txt的文件引用
        file_context = file_object.readlines()
        # file_context = byte_stream.decode('utf-8')

        xmlstr = ""
        for lineStr in tqdm(file_context, desc='正在读取：'):
            # datalist.append(lineStr)
            xmlstr = xmlstr + (lineStr.decode('utf-8').replace('\n', ''))
        return xmlstr
    finally:
        file_object.close()


def copy_file(srcfile, dstfile):
    import os
    import shutil
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    if os.path.isfile(dstfile):
        print("%s already exist!" % (srcfile))
    else:
        shutil.copy(srcfile, dstfile)  # 移动文件
        print("copy %s -> %s" % (srcfile, dstfile))


def remove_empty_dir(path):
    import os
    for (root, dirs, files) in os.walk(path, topdown=False):
        for item in dirs:
            dir = os.path.join(root, item)
            try:
                os.rmdir(dir)
                print(dir)
            except Exception as e:
                pass


