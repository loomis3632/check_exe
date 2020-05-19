# encoding: utf-8
# @File  : count_2gram_train.py
# @Author: xiangcaijiaozi
# @Date  : 2020/3/13 11:22
# @Desc  :用于训练（统计）ngram模型
# 先更新映射字典，再更新二维矩阵。最后进行存储。
import pickle
import re
import numpy as np
import chardet
import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 要调取其他目录下的文件。 需要在atm这一层才可以
sys.path.append(BASE_DIR)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filename='bigram_train_exe_log.log', filemode='w')


def get_all_path():
    """
    获取当前目录以及子目录下所有的.txt文件，
    :param open_file_path:
    :return:
    """
    # rootdir = open_file_path
    rootdir = os.getcwd()
    path_list = []
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        com_path = os.path.join(rootdir, list[i])
        if os.path.isfile(com_path) and com_path.endswith("input.txt"):
            path_list.append(com_path)
    return path_list


def get_encoding(file):
    """
    # 获取文件编码类型
    :param file: 文件路径
    :return: 编码
    """
    # 二进制方式读取，获取字节数据,不必全部read，检测编码类型
    with open(file, 'rb') as f:
        data = f.read(1024)
        return chardet.detect(data)['encoding']


def save_variable(v, filename):
    """
    用于保存变量
    :param v: 数据变量
    :param filename: 要保存的文件
    :return:
    """
    f = open(filename, 'wb')
    pickle.dump(v, f)
    f.close()
    return filename


def load_variable(filename):
    """
    # 读取保存的变量
    :param filename: 要读取的文件路径
    :return: 返回存储的数据
    """
    f = open(filename, 'rb')
    r = pickle.load(f)
    f.close()
    return r


def get_dict_map(stra, dict_map):
    """
    用于建立单字和序号的映射，使用字典，键：为字，值为序号
    :param stra: 字符串
    :param dict_map: 待更新的字典
    :return:
    """
    # 只保留汉字
    pattern = re.compile(r'[\u4e00-\u9fa5]')  # 中文的编码范围是：\u4e00到\u9fa5
    stringa = "".join(pattern.findall(stra))
    # 字典长度
    dict_map_index = len(dict_map)

    for ele in stringa:
        if ele not in dict_map:  # in的速度快于haskeys（）
            dict_map[ele] = dict_map_index
            dict_map_index += 1

    return dict_map


def update_matrix(stra, dict_map, matrix):
    """
    更新模型矩阵
    :param stra:
    :param dict_map:
    :param matrix:
    :return:
    """
    dict_map_length = len(dict_map)
    matrix_length = len(matrix)
    # 字符串处理，只保留汉字
    pattern = re.compile(r'[\u4e00-\u9fa5]')  # 中文的编码范围是：\u4e00到\u9fa5
    stringa = "".join(pattern.findall(stra))

    # 若二维矩阵与旧字典长度一样（二维矩阵建立的长度来自字典长度），说明没有新字添加进来。
    # 长度不一样，有新字添加进来，则扩展矩阵并把旧矩阵数值更新到新矩阵中再更新数值；
    # 长度一样，则没有新字添加进来，只需更旧矩阵数值。
    if matrix_length < dict_map_length:
        # numpy建立并初始化新的二维矩阵,此时的长度为新的dict_map的长度。
        matrix_new = np.zeros((dict_map_length, dict_map_length), dtype=np.int)
        # 把旧的矩阵数值更新到新的矩阵中
        for i in range(matrix_length):
            for j in range(matrix_length):
                matrix_new[i][j] = matrix[i][j]
        matrix = matrix_new

    # 把输入的字符串的字符统计更新到矩阵中
    for i in range(len(stringa)):
        i += 1
        if i == len(stringa):
            break
        # print(i)
        x = dict_map.get(stringa[i - 1])
        y = dict_map.get(stringa[i])
        if x != None and y != None:  # 为了防止查询不存在的字映射
            matrix[x][y] = matrix[x][y] + 1

    return matrix


def get_bigram_info(txt_path, dict_map, matrix):
    """
    获取符合要求的训练内容,并把字符串传给相应函数，获得bigarm的训练信息，包括字和序号的映射，二维矩阵
    :param txt_path:
    :return:
    """
    # dir = r'./model2/'
    coding = get_encoding(txt_path)
    with open(txt_path, 'r', encoding=coding, errors='ignore') as rf:
        res = ""
        file_content_flag = 0
        for line in rf:
            if line.startswith('<全文>='):
                line = line.replace('<全文>=', '')
                res = res + line
                file_content_flag = 1
            if file_content_flag == 1 and not line.startswith('<上传日期>='):
                res = res + line
            if file_content_flag == 1 and line.startswith('<上传日期>='):
                dict_map = get_dict_map(res, dict_map)
                # save_variable(dict_map, dir + r'dict_map.txt')
                # save_variable(len(dict_map), dir + r'dict_map_length.txt'
                matrix = update_matrix(res, dict_map, matrix)
                # save_variable(matrix, dir + 'matrix.txt')

                res = ""
                file_content_flag = 0

    return dict_map, matrix


def bigram_train():
    # dir = BASE_DIR + r'./model/'  # 存储模型等的文件夹
    dir = r'./model2/'  # 存储模型等的文件夹

    dict_map = load_variable(dir + 'dict_map.txt')  # 加载映射以及长度
    dict_map_length = load_variable(dir + 'dict_map_length.txt')
    matrix = load_variable(dir + 'matrix.txt')  # 加载二维矩阵
    count = 0
    count2 = 0

    path_lists = get_all_path()
    print(path_lists)
    for path in path_lists:
        coding = get_encoding(path)
        # 第一遍遍历用于更新字典映射
        with open(path, "r", encoding=coding, errors="ignore") as f:
            for ele in f:
                dict_map = get_dict_map(ele, dict_map)
                print(count)
                count += 1

        # 更新好的字典进行保存，在模型建立过程需要读取
        save_variable(dict_map, dir + r'dict_map.txt')
        save_variable(len(dict_map), dir + r'dict_map_length.txt')
        # 字典键值互换，
        # dict_map2 = dict(zip(dict_map.values(), dict_map.keys()))
        # save_variable(dict_map2, dir + r'dict_map2.txt')

        # 第二遍遍历用于建立模型，更新二维矩阵
        with open(path, "r", encoding=coding, errors="ignore") as f2:
            for ele in f2:
                matrix = update_matrix(ele, dict_map, matrix)
                count2 += 1
                print(count2)

        save_variable(matrix, dir + 'matrix.txt')


def bigram_train2():
    # dir = BASE_DIR + r'./model/'  # 存储模型等的文件夹
    dir = r'./model3/'  # 存储模型等的文件夹
    count = 0
    dict_map = load_variable(dir + 'dict_map.txt')  # 加载映射
    dict_map_length = load_variable(dir + 'dict_map_length.txt')
    matrix = load_variable(dir + 'matrix.txt')  # 加载二维矩阵
    path_lists = get_all_path()  # 获取所有的路径文件
    # print(path_lists)
    for path in path_lists:
        coding = get_encoding(path)
        with open(path, 'r', encoding=coding, errors='ignore') as rf:  # 读取语料文件的保存的路径文件
            for line in rf:
                line_split = line.split('\t')

                if len(line_split) >= 2:
                    txt_path = line_split[1].strip()  # 获取训练txt文件路径
                    if os.path.exists(txt_path):  # 训练文件存在，打开
                        count += 1
                        logging.info('正在处理第%s个文本；路径:%s' % (str(count), txt_path))
                        dict_map, matrix = get_bigram_info(txt_path, dict_map, matrix)
                        save_variable(dict_map, dir + r'dict_map.txt')
                        save_variable(len(dict_map), dir + r'dict_map_length.txt')
                        save_variable(matrix, dir + 'matrix.txt')


if __name__ == '__main__':
    # bigram_train()
    bigram_train2()
