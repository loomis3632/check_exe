# encoding: utf-8
"""
@File: bigram_check.py
@Author: xiangcaijiaozi
@Date: 2020/4/27 14:57
@Desc: 
"""
import pickle
import re
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 要调取其他目录下的文件。 需要在atm这一层才可以
sys.path.append(BASE_DIR)


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


# 加载二维矩阵等模型信息。
# dir = BASE_DIR + r'/model/'
dir = r'./model/'
matrix = load_variable('%s%s' % (dir, 'matrix.txt'))
matrix_line_sum = matrix.sum(axis=0)  # 一个字的行总的次数求和。
dict_map = load_variable('%s%s' % (dir, 'dict_map.txt'))


# num_char_map = load_variable(dir + r"dict_map2.txt")

def model_bigram(stringa, pro="0.0001-0.01"):
    """
    根据二维矩阵，判断分析输入的字符串，来发现低概率的字符存在的问题
    :param stra:
    :return:
    """
    # print stringa

    pattern = re.compile('[\u4e00-\u9fa5]')  # 中文的编码范围是：\u4e00到\u9fa5
    stra = "".join(pattern.findall(stringa))
    # print stra
    pro_list = pro.split("-")
    pro_min = float(min(pro_list))
    pro_max = float(max(pro_list))
    str_res = ""  # 要求的概率范围阈值之内的字符。
    new_str = ""  # 对于训练模型中未出现的词，视为新词，单独成一个新词结果。
    stra_length = len(stra)

    for i in range(stra_length):
        i += 1
        if (i <= stra_length - 2):
            # 对于检测的字符进行判断是否在字典中。思路：已训练的认为是正确的，字符不存在则认为是错误的。
            if (stra[i - 1] in dict_map) and (stra[i] in dict_map) and (stra[i + 1] in dict_map):
                x = dict_map[stra[i - 1]]
                y = dict_map[stra[i]]
                z = dict_map[stra[i + 1]]
                # 模型中stra[i]stra[i+1]的频数
                n = matrix[x][y]
                m = matrix_line_sum[x]
                k = matrix[y][z]
                t = matrix_line_sum[y]
                pro1 = n / m
                pro2 = k / t
                # print stra[i - 1], stra[i], stra[i + 1], n, m, k, t
                if (pro_min <= pro1 <= pro_max) and (pro_min <= pro2 <= pro_max):
                    # str_res = str_res + stra[i - 1] + stra[i] + stra[i + 1] + ";"
                    str_res = '%s%s%s%s%s' % (str_res, stra[i - 1], stra[i], stra[i + 1], ";")
            else:
                # str_res = str_res + stra[i - 1] + stra[i] + stra[i + 1] + ";"
                new_str = '%s%s%s%s%s' % (new_str, stra[i - 1], stra[i], stra[i + 1], ";")

    return str_res, new_str


if __name__ == '__main__':
    stra = "跶基于象素点跶转移图象合成的若干关键技术研究跶"
    pro = "0.0001-0.01"
    res, new_str = model_bigram(stra, pro)
    print(res)
    print("------新词------")
    print(new_str)
