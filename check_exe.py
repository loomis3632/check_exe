import sys, os

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
import re
from threading import Thread
import chardet
import logging
import regular_check
import bigram_check

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 要调取其他目录下的文件。 需要在atm这一层才可以
sys.path.append(BASE_DIR)
sys.path.append(BASE_DIR + r'/check')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filename='check_exe.log', filemode='w')

dir = r"./model/"


class MyThread(Thread):
    """
    继承Thread类，重新定义run函数，定义获取线程结果的函数
    """

    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


def get_stopwords():
    """
    获取停止词，修改全局变量stopwords_set
    :return:
    """
    global count
    count += 1
    print(count)
    txt_path = dir + r"cn_stopwords.txt"
    global stopwords_set
    with open(txt_path, 'r', encoding="utf-8", errors='ignore') as rf:
        for line in rf:
            line_pro = line.strip()
            if line_pro not in stopwords_set:
                stopwords_set.add(line_pro)
    return stopwords_set

# 获取停止词
count = 0
stopwords_set = set()
get_stopwords()
print(stopwords_set)


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
        bigram_error_res = ""
        bigram_error_temp = ""
        bigram_new_res = ""
        bigram_new_temp = ""
        file_content_flag = 0
        file_name = ""
        for line in rf:
            if line.startswith('<篇名>='):
                file_name = line[5:]
            if line.startswith('<全文>='):
                line = line.replace('<全文>=', '')
                res = res + line
                file_content_flag = 1

            if file_content_flag == 1 and not line.startswith('<上传日期>='):
                res = res + line
                # print(line)
                lineLists = re.split('[，,.。？?]', line.strip())
                for ele in lineLists:
                    # ngram检测
                    str_res, new_str = bigram_check.model_bigram(ele, "0.0001-0.001")
                    if len(str_res) > 1:  # 错词语
                        char_temp = str_res[1]
                        if char_temp not in stopwords_set:


                            bigram_error_res =  ('%s%s%s%s%s' % (bigram_error_res, str_res,"-->",ele,"\n"))
                        # print(bigram_error_res)
                        # print("error_words:" + str_res + "----->>" + ele)
                    if len(new_str) > 0:  # 新词语
                        bigram_new_res = ('%s%s%s%s%s' % (bigram_new_res, new_str, "-->", ele, "\n"))
                        # print("new_words:" + new_str + "----->>" + ele)
                        # print(bigram_new_res)


            if file_content_flag == 1 and line.startswith('<上传日期>='):
                print(bigram_error_res)
                print(bigram_new_res)
                # print(res)
                # 规则检测
                # regular_res = regular_check.regular_check(res, size=100, interval=50, ratio=4,
                #                                           regular_index=[1, 5, 2, 4, 3], one_pattern="")
                # # ngram检测
                # str_res, new_str = bigram_check.model_bigram(res, "0.0001-0.001")
                # 写入，规范表明错误类型

                # threads = []
                # # (res, size=100, interval=50, ratio=5,regular_index=[1, 5, 2, 4, 3], one_pattern="")
                # t1 = MyThread(regular_check.regular_check, args=(res, 100, 50, 4, [1, 5, 2, 4, 3], ""))
                # threads.append(t1)
                # # (res, "0.001-0.01")
                # t2 = MyThread(bigram_check.model_bigram, args=(res, "0.0001-0.001"))
                # threads.append(t2)
                # for t in threads:
                #     t.start()
                # for tt in threads:
                #     tt.join()
                # regular_res = t1.get_result()
                # str_res, new_str = t2.get_result()

                # if "regular_check:Normal" not in regular_res:
                #     print(regular_res)
                #     re_wf.write('%s%s%s%s%s' % (txt_path, "--", file_name, regular_res, '\n'))
                # if len(str_res) > 0:
                #     bi_wf1.write('%s%s%s%s%s' % (txt_path, "--", file_name, str_res, '\n'))
                # if len(new_str) > 0:
                #     bi_wf2.write('%s%s%s%s%s' % (txt_path, "--", file_name, new_str, '\n'))

                res = ""
                bigram_error_res = ""
                bigram_new_res = ""
                file_content_flag = 0
                file_name = ""


def check():
    """
    :return:
    """
    path_lists = get_all_path()
    count = 0
    for path in path_lists:
        coding = get_encoding(path)
        with open(path, 'r', encoding=coding, errors='ignore') as rf:  # 读取语料文件的保存的路径文件
            for line in rf:
                line_split = line.split('\t')
                if len(line_split) >= 2:  # 越界
                    txt_path = line_split[1].strip()  # 获取训练txt文件路径
                    if os.path.exists(txt_path):  # 训练文件存在，打开文件
                        count += 1
                        logging.info('正在处理第%s个文本；路径:%s' % (str(count), txt_path))
                        print(count, txt_path)
                        get_check_res(txt_path)


if __name__ == '__main__':
    check()
