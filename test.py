# encoding: utf-8
"""
@File: test.py
@Author: xiangcaijiaozi
@Date: 2020/5/18 10:12
@Desc: 
"""
import re


def test(a):
    a += 1
    return a


def test1(a):
    print("test1" + str(a))
    for i in range(3):
        a = test(a)
        print(a, id(a))
    print("test1" + str(a))


def test2():
    a = 5
    test1(a)
    print("test2" + str(a))


def split_test():
    txt_path = r"E:\dataset\check_test_data\txt_test.txt"
    with open(txt_path, 'r', encoding="utf-8", errors='ignore') as rf:
        for line in rf:
            lineLists = re.split('[，,.。？?]', line.strip())
            print(lineLists)


def get_stopwords():
    txt_path = "./model/" + r"cn_stopwords.txt"
    stopwords_set = set()
    with open(txt_path, 'r', encoding="utf-8", errors='ignore') as rf:
        for line in rf:
            line_pro = line.strip()
            if line_pro not in stopwords_set:
                stopwords_set.add(line_pro)
    print(stopwords_set)
    return stopwords_set

def count_test():
    global count
    count+=1
    print(count)
count =0

def str_test():
    stra = "跶基于象素点跶转移图象合成的若干关键技术研究跶,"
    for i in range(len(stra)-2):
        x = stra[i ]
        y = stra[i+1]
        z = stra[i +2]
        print(x,y,z)



if __name__ == '__main__':
    # test2()
    # split_test()
    # get_stopwords()
    # count_test()
    str_test()