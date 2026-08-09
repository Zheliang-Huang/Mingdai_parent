import json
import os
import platform
from common.fileutils import *
from common.excel_utils import *


def parse_OCR_json(json_format):
    unique_values = set()
    char_location_list = []
    # 正文解析
    # if json_format["referenceSignInstances"] is None:
    #     return 0
    if len(json_format["referenceSignInstances"]) == 0:
        return char_location_list
    if len(json_format["referenceSignInstances"]["正文"]) != 0:
        main = json_format['referenceSignInstances']["正文"]
        if type(main) is dict:
            for line in main['original_position']:
                # # 正文成分标签与坐标
                # component_word = '正文'
                # component_points = line.get('points')
                # component_location = str(int(component_points[0][0]))+ ' ' +str(int(component_points[0][1]))+ ' ' +str(int(component_points[2][0]))+ ' ' +str(int(component_points[2][1]))
                # component = component_location + ' ' + component_word
                # if component not in unique_values:
                #     char_location_list.append(component)
                #     unique_values.add(component)
                for charline in line['charlines']:
                    # 获取成分
                    component_word = '正文'
                    component_points = charline.get('points')
                    component_location = str(int(component_points[0][0])) + ' ' + str(
                        int(component_points[0][1])) + ' ' + str(
                        int(component_points[2][0])) + ' ' + str(int(component_points[2][1]))
                    component = component_location + ' ' + component_word
                    if component not in unique_values:
                        # char_location_list.append(component)
                        unique_values.add(component)
                    # 判断大小字
                    if 'font_size' in charline and charline['font_size'] == 'large':
                        for text in charline['texts']:
                            word = text['word']
                            bbox = text['char_bbox']
                            char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                            if char not in unique_values:
                                char_location_list.append(char)
                                unique_values.add(char)
                    if 'font_size' in charline and charline['font_size'] == 'small':
                        for text in charline['texts']['small_print']:
                            word = text['word']
                            bbox = text['char_bbox']
                            char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                            if char not in unique_values:
                                char_location_list.append(char)
                                unique_values.add(char)
                    if 'font_size' in charline and charline['font_size'] == 'media':
                        for text in charline['texts']:
                            word = text['word']
                            bbox = text['char_bbox']
                            char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                            if char not in unique_values:
                                char_location_list.append(char)
                                unique_values.add(char)
        elif type(main) is list:
            for main_dict in main:
                if 'original_position' in main_dict:
                    for line in main_dict['original_position']:
                        # 正文成分标签与坐标
                        # component_word = '正文'
                        # component_points = line.get('points')
                        # component_location = str(int(component_points[0][0]))+ ' ' +str(int(component_points[0][1]))+ ' ' +str(int(component_points[2][0]))+ ' ' +str(int(component_points[2][1]))
                        # component = component_location + ' ' + component_word
                        # if component not in unique_values:
                        #     char_location_list.append(component)
                        #     unique_values.add(component)
                        for charline in line['charlines']:
                            # 获取成分
                            component_word = '正文'
                            component_points = charline.get('points')
                            component_location = str(int(component_points[0][0])) + ' ' + str(
                                int(component_points[0][1])) + ' ' + str(
                                int(component_points[2][0])) + ' ' + str(int(component_points[2][1]))
                            component = component_location + ' ' + component_word
                            if component not in unique_values:
                                # char_location_list.append(component)
                                unique_values.add(component)
                            # 判断大小字
                            if 'font_size' in charline and charline['font_size'] == 'large':
                                for text in charline['texts']:
                                    word = text['word']
                                    bbox = text['char_bbox']
                                    char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                        int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                                    if char not in unique_values:
                                        char_location_list.append(char)
                                        unique_values.add(char)
                            if 'font_size' in charline and charline['font_size'] == 'small':
                                for text in charline['texts']['small_print']:
                                    word = text['word']
                                    bbox = text['char_bbox']
                                    char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                        int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                                    if char not in unique_values:
                                        char_location_list.append(char)
                                        unique_values.add(char)
    # 表格解析
    if len(json_format["referenceSignInstances"]["表格"]) != 0:
        for row in json_format["referenceSignInstances"]["表格"]:
            for cell in row['blocks']:
                # 表格成分标签与坐标
                cell_name = '表格正文'
                cell_location = str(int(cell['xmin'])) + ' ' + str(int(cell['ymin'])) + ' ' + str(
                    int(cell['xmax'])) + ' ' + str(int(cell['ymax'])) + ' ' + cell_name
                if cell_location not in unique_values:
                    # char_location_list.append(cell_location)
                    unique_values.add(cell_location)
                if 'original_position' in cell and len(cell['original_position']) != 0:
                    for original_position in cell['original_position']:
                        for charline in original_position['charlines']:
                            # 判断大小字
                            if 'font_size' in charline and charline['font_size'] == 'large':
                                for text in charline['texts']:
                                    word = text['word']
                                    bbox = text['char_bbox']
                                    char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                        int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                                    if char not in unique_values:
                                        char_location_list.append(char)
                                        unique_values.add(char)
                            if 'font_size' in charline and charline['font_size'] == 'small':
                                for text in charline['texts']['small_print']:
                                    word = text['word']
                                    bbox = text['char_bbox']
                                    char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                        int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                                    if char not in unique_values:
                                        char_location_list.append(char)
                                        unique_values.add(char)
    # 天头解析
    if len(json_format["referenceSignInstances"]["天头"]) != 0:
        main = json_format['referenceSignInstances']["天头"]
        if type(main) is dict:
            for line in main['original_position']:
                for charline in line['charlines']:
                    # 获取成分
                    component_word = '天头'
                    component_points = charline.get('points')
                    component_location = str(int(component_points[0][0])) + ' ' + str(
                        int(component_points[0][1])) + ' ' + str(
                        int(component_points[2][0])) + ' ' + str(int(component_points[2][1]))
                    component = component_location + ' ' + component_word
                    if component not in unique_values:
                        # char_location_list.append(component)
                        unique_values.add(component)
                    # 判断大小字
                    if 'font_size' in charline and charline['font_size'] == 'large':
                        for text in charline['texts']:
                            word = text['word']
                            bbox = text['char_bbox']
                            char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                            if char not in unique_values:
                                char_location_list.append(char)
                                unique_values.add(char)
                    if 'font_size' in charline and charline['font_size'] == 'small':
                        for text in charline['texts']['small_print']:
                            word = text['word']
                            bbox = text['char_bbox']
                            char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                            if char not in unique_values:
                                char_location_list.append(char)
                                unique_values.add(char)
    if '版心' in json_format["layoutAnalysis"]:
        for banxin in json_format["layoutAnalysis"]["版心"]:
            component_word = '版心'
            component_location = str(int(banxin[0])) + ' ' + str(
                int(banxin[1])) + ' ' + str(int(banxin[2])) + ' ' + str(int(banxin[3]))
            component = component_location + ' ' + component_word
            if component not in unique_values:
                # char_location_list.append(component)
                unique_values.add(component)
    return char_location_list


def run(src, charnum_file):
    source = src
    excel_out = charnum_file
    excel_list = []
    print(source)

    total_num = 0
    print('开始遍历子文件夹')
    book_num = 1
    for each_book in os.listdir(source):
        num = 0

        print(each_book, '已完成：{}，共{}'.format(book_num, len(os.listdir(source))))
        full_path_each = os.path.join(source, each_book)
        if os.path.isdir(full_path_each):
            pic_list = []
            traverse_dir(full_path_each, pic_list, ['.png', '.tiff', '.jpg', '.bmp', '.jpeg'])
            for pic in pic_list:
                if 'pageimages' in pic:
                    num += 1
            total_num += num

            json_list = []
            traverse_dir(full_path_each, json_list, ['.json'])
            char_num = 0
            for json_path in json_list:
                # print(json_path)
                json_read = read_txt_file(json_path, 'utf-8')
                json_get = json.loads(json_read)
                if json_get is not None and json_get['code'] == 200:
                    json_content = json_get['Images']
                    char_list = parse_OCR_json(json_content)
                    char_num += len(char_list)
            excel_list.append(['', each_book.split(' ')[0], each_book.split(' ')[1], str(char_num), str(num)])
        book_num += 1
    print('输出完成，共计', total_num, '张图片')
    create_excel(['元数据id', '著录号', '书名', '字数', '图片数量'], excel_list, excel_out)