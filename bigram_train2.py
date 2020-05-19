# @File  : bigram_train_exe.py
# @Author: xiangcaijiaozi
# @Date  : 2020/3/13 11:22
# @Desc  :用于训练（统计）ngram模型
# 先更新映射字典，再更新二维矩阵。最后进行存储。
import pickle
import re
import numpy as np
import time
import chardet
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 要调取其他目录下的文件。 需要在atm这一层才可以
sys.path.append(BASE_DIR)


def get_all_path(open_file_path):
    """
    获取当前目录以及子目录下所有的.txt文件，
    :param open_file_path:
    :return:
    """
    rootdir = open_file_path
    path_list = []
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        com_path = os.path.join(rootdir, list[i])
        if os.path.isfile(com_path) :
            path_list.append(com_path)
        if os.path.isdir(com_path):
            path_list.extend(get_all_path(com_path))
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


# 加载变量，作为全局变量
# dict_map = load_variable('./model_test/dict_map.txt')  # 加载映射以及长度
# dict_map_length = load_variable('./model_test/dict_map_length.txt')
# matrix = load_variable('./model_test/matrix.txt')  # 加载二维矩阵


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
    # 二维矩阵模型更新
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


def bigram_train(rootdir):
    """
    模型训练
    :param rootdir: 训练集文件夹
    :return:
    """
    # dir = BASE_DIR + r'/model2/'  # 存储模型等的文件夹
    dir = r'./model2/'  # 存储模型等的文件夹
    # path = r"E:\zhcrosscorpus\zhcrosscorpus.txt"  # 语料

    dict_map = load_variable(dir + 'dict_map.txt')  # 加载映射以及长度
    dict_map_length = load_variable(dir + 'dict_map_length.txt')
    matrix = load_variable(dir + 'matrix.txt')  # 加载二维矩阵
    count = 0
    count2 = 0

    path_lists = get_all_path(rootdir)
    for path in path_lists:
        print(count)
        count += 1
        coding = get_encoding(path)
        # 第一遍遍历用于更新字典映射
        with open(path, "r", encoding=coding, errors="ignore") as f:
            for ele in f:
                dict_map = get_dict_map(ele, dict_map)

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
        save_variable(matrix, dir + 'matrix.txt')



if __name__ == '__main__':
    # rootdir = r'E:\dataset\语料\zhcrosscorpus.txt'
    # rootdir = r'E:\dataset\test1'
    rootdir = r'E:\dataset\wiki_zh_2019\wiki_zh'
    bigram_train(rootdir)
