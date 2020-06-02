# @File  : regular_check_extend.py
# @Author: xiangcaijiaozi
# @Date  : 2019/10/8 11:24
# @Desc  : 对输入的字符串检测
import re
import csv
import jieba_fast as jieba
import char_count2

dir = r"./model2/"  # 存放所需文件的文件夹，与该py文件同级目录


def get_engset():
    """
    将英文字典加载内存，存储到全局变量engset集合，
    :return: set集合的英文单词。
    """
    global engset
    csv_path = dir + 'engdict.csv'
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i in reader:
            engset.add(i[0])


engset = set()  # 全局变量
get_engset()


def del_num_most(one_dict):
    """用于删除数字占比较高的字符串，在此统计的事字符串各个字符的数目，先去空格。
    :param one_dict:
    :return:
    """
    num, char, space, others = 0, 0, 0, 0  # 分别统计数字、字母、空格、其他字符个数

    for key in list(one_dict):
        stra = one_dict[key]
        stra_pro = stra.replace(' ', '')
        stra_pro_length = len(stra_pro)  # 去掉空格后的字符串长度
        for i in stra:
            if i.isdigit():
                num = num + 1
            elif i.encode('utf-8').isalpha():  # 汉字识别为字符，进行转换
                char = char + 1
            elif i == ' ':
                space = space + 1
            else:
                others = others + 1
        # print(num, char, space, others)
        if num >= stra_pro_length * 0.5:  # 数字数目的占比
            one_dict.pop(key)
        if stra_pro.isalnum():  # 全字母和数字
            if key in one_dict:
                one_dict.pop(key)

    return one_dict


def del_gene_order(one_dict):
    """
    删除基因序列，单独删除，是因为占比很高，特殊处理。
    :param one_dict:
    :return:
    """
    for key in list(one_dict):
        stra = one_dict[key]
        count1 = stra.count("A")
        count2 = stra.count("C")
        count3 = stra.count("G")
        count4 = stra.count("T")
        length = len(stra)
        count_sum = count1 + count2 + count3 + count4
        if count_sum >= length * 0.5:
            one_dict.pop(key)

    return one_dict


def filter_catalog(one_dict):
    """
    过滤目录
    :param one_dict: 字典
    :return: 返回过滤后的字典
    """
    one_pattern = r'([………,‥]{2,})|([‥,… ,┈ ,--,/]{3,})|([,=]{4,})|([・,.,．,─,― ,―,·,_, ―,-,. ,—,· ,。,*,/,x,|,＿]{7,})'
    pattern = re.compile(one_pattern)

    for key in list(one_dict):
        res = pattern.search(one_dict[key])
        if res:
            one_dict.pop(key)

    return one_dict


def filter_engdict(one_dict):
    """
    过滤英文单词
    :param one_dict:
    :return:
    """
    for key in list(one_dict):
        seg_res = jieba.cut(one_dict[key], cut_all=True)  # 分词
        value_seg = [i for i in list(seg_res) if i != '']  # 去空元素
        value_seg_length = len(value_seg)

        value_filter = list(filter(lambda x: x in engset, value_seg))  # 查询单词是否是英文单词
        value_filter_length = len(value_filter)

        if value_filter_length >= value_seg_length * 0.5:  # 英文单词超过一半
            one_dict.pop(key)

    return one_dict


def filter_number(one_dict):
    """
    过滤数字，整数、小数多为实验数据
    :param one_dict:
    :return:
    """
    # one_pattern = r"\d+(\.\d+)?"
    one_pattern = r"\d+\.?\d*"  # 修改后的
    pattern = re.compile(one_pattern)

    for key in list(one_dict):
        value_length = len(one_dict[key].split())
        res = pattern.findall(one_dict[key])
        res = [i for i in res if i != '']
        res_length = len(res)

        if value_length * 0.6 <= res_length:
            one_dict.pop(key)

    return one_dict


def filter_alphabet(one_dict):
    """
    过滤字母，多为基因序列等
    :param one_dict:
    :return:
    """
    one_pattern = r'[a-zA-Z]{3,}'
    pattern = re.compile(one_pattern)

    for key in list(one_dict):
        max_char = key.split("-")[-1]  # 获取最大的字符

        if max_char.isalpha():  # 判断字符是否是英文字符，若不是则不处理，因为如??????adfadsf
            re_res = pattern.findall(one_dict[key])
            re_res_length = len(re_res)

            seg_res = jieba.cut(one_dict[key].strip(), cut_all=True)
            seg_res_list = list(seg_res)
            seg_res_list = [i for i in seg_res_list if i != '']
            seg_res_list_length = len(seg_res_list)

            if seg_res_list_length == 0:
                continue
            elif seg_res_list_length * 0.5 <= re_res_length:
                one_dict.pop(key)

    return one_dict


def filter_chinese_words(one_dict):
    """
    过滤并列的中文字符。如：木头、石头、骨头、舌头、罐头、苗头、
    :param one_dict:
    :return:
    """
    one_pattern = r"([\u4e00-\u9fa5]+(、|，)){5,}"
    pattern = re.compile(one_pattern)

    for key in list(one_dict):
        res = pattern.findall(one_dict[key])
        if len(res) > 0:
            one_dict.pop(key)

    return one_dict


def filter_user_defined(one_dict, one_pattern):
    """
    用户定义的正则表达式，进行过滤
    :param one_dict:
    :param one_pattern:
    :return:
    """
    pattern = re.compile(one_pattern)

    for key in list(one_dict):
        res = pattern.findall(one_dict[key])
        if len(res) > 0:
            one_dict.pop(key)

    return one_dict


def regular_check(one_string="", size=100, interval=50, ratio=5, regular_index=None, one_pattern=""):
    """
    检测字符串。
    :param one_string: 输入字符串
    :param size: 窗口大小，默认100
    :param interval: 步长，默认50
    :param ratio: 比例，默认5
    :param li: 采用的规则过滤，一共[1, 2, 3, 4, 5]五条
    :param one_pattern: 用户自定义的正则表达式
    :return: 字典，key：位置和最大字符的字符串；value：检测有问题的子字符串
    """
    check_res = char_count2.char_count(one_string, size, interval, ratio)
    func_index = [1, 2, 3, 4, 5]

    if not regular_index:
        regular_index = [1, 2, 3, 4, 5]
    else:
        regular_index = list(set(regular_index) & set(func_index))  # 求交集，用于参数检查
    if len(check_res) != 0:
        check_res = del_num_most(check_res)  # 先对统计结果过滤，过滤大部分不符合要求的数字和字母
        check_res = del_gene_order(check_res)

        for index in regular_index:
            if index == 1:
                check_res = filter_catalog(check_res)
                # print("1-catalog")

            elif index == 2:
                check_res = filter_engdict(check_res)
                # print("2-engdict")

            elif index == 3:
                check_res = filter_number(check_res)
                # print("3-number")

            elif index == 4:
                check_res = filter_alphabet(check_res)
                # print("4-alphabet")

            elif index == 5:
                check_res = filter_chinese_words(check_res)
                # print("5-chinese_characters")

        if one_pattern != "":
            check_res = filter_user_defined(check_res, one_pattern)
            # print("6-user_defined")

    if check_res:
        return check_res
    else:
        return "regular_check:Normal"


if __name__ == '__main__':
    # one_string = "发ssssssssssssssssssssssssssssssssssssssss现应该是因为python2.x的默认编码是ascii，而代码中可能由utf-8的字符导致，解决方法是设置utf-8。"
    one_string = "khasds中文中文中文中文中文中文中国12367890,.，。、,中中中中中中中中中中中中中中中中中中Jér?me中文"
    res = regular_check(one_string, size=100, interval=50, ratio=5, regular_index=[1, 5, 2, 4, 3], one_pattern="")
    # txt_path = r"E:\pycharm_pro/check_exe/regular_check_exe_res.txt"
    # coding = get_encoding(txt_path)
    # print(coding)
    # with open(txt_path, 'r', encoding=coding, errors='ignore') as rf:
    #     count = 0
    #     for line in rf:
    #         count += 1
    #         if count <= 100:
    #             res = regular_check(line, size=100, interval=50, ratio=5, regular_index=[1, 5, 2, 4, 3], one_pattern="")
    #             if res != "regular_check:Normal":
    #                 # print(type(res),res)
    #                 pass
