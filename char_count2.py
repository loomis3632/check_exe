# @File  : regular_check_extend.py
# @Author: xiangcaijiaozi
# @Date  : 2019/10/8 11:24
# @Desc  : 对输入的字符串统计
import re
from collections import Counter


# 字符串最大字符统计
def max_char_number(one_string):
    """
    使用Counter统计字符串的最大字符
    :param str:要计算的字符串
    :return:返回频数最多的字符和词频,以及该字符串
    """
    one_string_pro = re.sub(r"\s+", "", one_string)
    res = Counter(one_string_pro)
    max_info = res.most_common(1)  # 获取最大的字符的元组信息
    if len(res) > 0:
        max_char = max_info[0][0]  # 最大的字符
        max_number = max_info[0][1]  # 最大的字符数目
    else:
        max_char = " "
        max_number = 0

    return max_char, max_number, one_string


def char_count(one_string, size, interval, ratio):
    """
    :param one_string: 要检测的字符串
    :param size: 一次检测的字符串长度大小，即窗口大小
    :param interval: 步长
    :param ratio: 最大字符占比
    :return: 检测结果有错的子字符串
    """
    one_string = re.sub(r'[\n\t\r]', '', one_string)
    one_string_length = len(one_string)
    first = 0  # 起始位置
    res_dict = dict()
    dict_index = 0
    diff = size  # 用于补齐字符串末端字符不全

    while (size < one_string_length + diff):
        one_string_part = one_string[first:size]  # 若字符串长度小于size，则size就是长度的位置
        one_string_part_length = len(one_string_part)
        one_string_part_index = one_string.find(one_string_part)

        if one_string_part_length >= 20:  # 最低的检测字符数
            max_char, max_number, one_string_part_re = max_char_number(one_string_part)
            if max_number * ratio > one_string_part_length:
                dict_index = str(dict_index) + "-" +str(one_string_part_index)+"-"+ max_char
                res_dict[dict_index] = one_string_part
                dict_index = int(dict_index.split("-")[0])
                dict_index += 1

        first = interval + first
        size = interval + size

    return res_dict



