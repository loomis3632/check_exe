import sys
import os
import chardet
import regular_check
import bigram_check

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 要调取其他目录下的文件。 需要在atm这一层才可以
sys.path.append(BASE_DIR)


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


def get_check_res(txt_path):
    """

    :param txt_path:
    :return:
    """
    regular_path = r"./regular_res.txt"
    bigram_path1 = r"./bigram_error.txt"
    bigram_path2 = r"./bigram_new.txt"

    coding = get_encoding(txt_path)
    with open(txt_path, 'r', encoding=coding, errors='ignore') as rf, \
            open(regular_path, 'a', encoding='utf-8', errors='ignore') as re_wf, \
            open(bigram_path1, 'a', encoding='utf-8', errors='ignore') as bi_wf1, \
            open(bigram_path2, 'a', encoding='utf-8', errors='ignore') as bi_wf2:
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
                print(res)
                # 规则检测
                regular_res = regular_check.regular_check(res, size=100, interval=50, ratio=5,
                                                                 regular_index=[1, 5, 2, 4, 3], one_pattern="")
                # ngram检测
                str_res, new_str = bigram_check.model_bigram(res, "0.001-0.01")
                # 写入，规范表明错误类型
                re_wf.write('%s%s%s' % (txt_path, ";", regular_res))
                bi_wf1.write('%s%s%s' % (txt_path, ";", str_res))
                bi_wf2.write('%s%s%s' % (txt_path, ";", new_str))

                res = ""
                file_content_flag = 0


def check():
    """
    :return:
    """
    path_lists = get_all_path()
    for path in path_lists:
        coding = get_encoding(path)
        with open(path, 'r', encoding=coding, errors='ignore') as rf:  # 读取语料文件的保存的路径文件
            for line in rf:
                line_split = line.split('\t')
                if len(line_split) >= 2:  # 越界
                    txt_path = line_split[1].strip()  # 获取训练txt文件路径
                    if os.path.exists(txt_path):  # 训练文件存在，打开文件
                        get_check_res(txt_path)


if __name__ == '__main__':
    check()
