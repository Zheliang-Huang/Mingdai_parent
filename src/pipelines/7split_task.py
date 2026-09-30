import json
import random
import os

from src.common.excel_utils import *
from src.common.fileutils import *


def parse_OCR_json(json_format, red_list):
    unique_values = set()
    char_location_list = []
    confident_dic = {}

    # 正文解析
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
                            confident = (text.get('topk').get(word)) * 100
                            if confident < 99:
                                red_list.append(word)
                            if confident < 90:
                                confident_dic[word] = confident

                            char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                            if char not in unique_values:
                                char_location_list.append(char)
                                unique_values.add(char)
                    if 'font_size' in charline and charline['font_size'] == 'small':
                        for text in charline['texts']['small_print']:
                            word = text['word']
                            bbox = text['char_bbox']
                            confident = (text.get('topk').get(word)) * 100
                            if confident < 99:
                                red_list.append(word)
                            if confident < 90:
                                confident_dic[word] = confident
                            char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                            if char not in unique_values:
                                char_location_list.append(char)
                                unique_values.add(char)
                    if 'font_size' in charline and charline['font_size'] == 'media':
                        for text in charline['texts']:
                            word = text['word']
                            bbox = text['char_bbox']
                            confident = (text.get('topk').get(word)) * 100
                            if confident < 99:
                                red_list.append(word)
                            if confident < 90:
                                confident_dic[word] = confident
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
                                    confident = (text.get('topk').get(word)) * 100
                                    if confident < 99:
                                        red_list.append(word)
                                    if confident < 90:
                                        confident_dic[word] = confident
                                    char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                        int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                                    if char not in unique_values:
                                        char_location_list.append(char)
                                        unique_values.add(char)
                            if 'font_size' in charline and charline['font_size'] == 'small':
                                for text in charline['texts']['small_print']:
                                    word = text['word']
                                    bbox = text['char_bbox']
                                    confident = (
                                                    text.get('topk').get(word)) * 100
                                    if confident < 99:
                                        red_list.append(word)
                                    if confident < 90:
                                        confident_dic[word] = confident
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
                                    confident = (text.get('topk').get(word)) * 100
                                    if confident < 99:
                                        red_list.append(word)
                                    if confident < 90:
                                        confident_dic[word] = confident
                                    char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                        int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                                    if char not in unique_values:
                                        char_location_list.append(char)
                                        unique_values.add(char)
                            if 'font_size' in charline and charline['font_size'] == 'small':
                                for text in charline['texts']['small_print']:
                                    word = text['word']
                                    bbox = text['char_bbox']
                                    confident = (text.get('topk').get(word)) * 100
                                    if confident < 99:
                                        red_list.append(word)
                                    if confident < 90:
                                        confident_dic[word] = confident
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
                            confident = (text.get('topk').get(word)) * 100
                            if confident < 99:
                                red_list.append(word)
                            if confident < 90:
                                confident_dic[word] = confident
                            char = str(int(bbox[0][0])) + ' ' + str(int(bbox[0][1])) + ' ' + str(
                                int(bbox[2][0])) + ' ' + str(int(bbox[2][1])) + ' ' + word
                            if char not in unique_values:
                                char_location_list.append(char)
                                unique_values.add(char)
                    if 'font_size' in charline and charline['font_size'] == 'small':
                        for text in charline['texts']['small_print']:
                            word = text['word']
                            bbox = text['char_bbox']
                            confident = (text.get('topk').get(word)) * 100
                            if confident < 99:
                                red_list.append(word)
                            if confident < 90:
                                confident_dic[word] = confident
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
    return char_location_list, confident_dic


def run(src, json_extract_dir, charnum_file, task_file):
    excel_list = []
    source = src
    excel_path = charnum_file
    output = task_file
    print(source)

    zsk_list = read_excel(excel_path, col_num=1)
    total_num = 0
    print('开始遍历子文件夹')
    if not os.path.isdir(json_extract_dir):
        os.makedirs(json_extract_dir)
    num = 1
    for each_book in os.listdir(source):
        zsk_num = each_book.split(' ')[0]
        if zsk_num not in zsk_list:
            print('不在本次任务清单内')
            num += 1
            continue
        print('已完成：{}，共{}'.format(num, len(os.listdir(source))))
        full_path_each = os.path.join(source, each_book)
        if os.path.isdir(full_path_each):
            json_list = []
            traverse_dir(full_path_each, json_list, ['.json'])
            json_path_dic = {os.path.basename(path):path for path in json_list}
            char_num = 0
            red_num = 0
            json_task_list = []
            if_confident_list = []
            json_output = []
            for json_path in json_list:
                json_name = os.path.basename(json_path)
                try:
                    json_read = read_txt_file(json_path, 'utf-8')
                    json_get = json.loads(json_read)
                    if json_get is not None:
                        json_content = json_get['Images']
                        red_list = []
                        char_list, confident_dic = parse_OCR_json(json_content, red_list)
                        if len(confident_dic) != 0:
                            if_confident_list.append(json_name)
                        red_num += len(red_list)
                        char_num += len(char_list)
                        if char_num >= 50000:
                            json_task_list.append(os.path.basename(json_path))
                            idx = 0
                            if len(if_confident_list) != 0:
                                while idx < 3:
                                    json_select = if_confident_list[random.randrange(0, len(if_confident_list))]
                                    copy_file(json_path, os.path.join(json_extract_dir, json_select))
                                    json_output.append(json_select)
                                    idx += 1
                            excel_list.append([zsk_num, ','.join(json_task_list), char_num, red_num, ','.join(json_output)])
                            json_output = []
                            if_confident_list = []
                            json_task_list = []
                            char_num = 0
                            red_num = 0
                        else:
                            json_task_list.append(os.path.basename(json_path))


                except Exception as exc:

                    raise RuntimeError(

                        f"处理JSON失败：{json_path}，"

                        f"错误原因：{exc}"

                    ) from exc
            if len(json_task_list) != 0:
                if len(if_confident_list) != 0:
                    sample_count = min(
                        3,
                        len(if_confident_list)
                    )

                    selected_jsons = random.sample(
                        if_confident_list,
                        sample_count
                    )
                    for json_select in selected_jsons:
                        json_path = json_path_dic[json_select]
                        copy_file(json_path, os.path.join(json_extract_dir, json_select))
                        json_output.append(json_select)
                excel_list.append([zsk_num, ','.join(json_task_list), char_num, red_num, ','.join(json_output)])
            num += 1
    create_excel(['任务标题', '处理范围', '任务量(千字)', '标红数量', '置信度json'], excel_list, output)


