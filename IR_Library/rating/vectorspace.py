import pandas as pd
import numpy as np
import math
import re
import unicodedata

book_info = pd.read_json('Book_info.json', encoding='utf-8')
book_info.head()


def Dic_building(a):
    contents = book_info[a].to_numpy()
    lst_contents = []
    dictionary = set()
    if a != 'TOPIC':
        for content in contents:
            if content is None: continue
            words = content.replace('"', '').replace('.', '').replace("'", "").replace(":", "").split()
            for i, word in enumerate(words):
                words[i] = unicodedata.normalize('NFC', word)
            lst_contents.append(words)
            dictionary.update(words)
    else:
        for content in contents:
            if content is None: continue
            s = ''
            for i in content:
                s = s + i
            words = s.replace('"', '').replace('.', '').replace("'", "").split()
            for j, word in enumerate(words):
                words[j] = unicodedata.normalize('NFC', word)
            lst_contents.append(words)
            dictionary.update(words)
    dictionary = list(dictionary)
    return contents, lst_contents, dictionary


# Xây dựng Inverted File
def build_inverted_files(dictionary, lst_contents):
    inv_files = dict()
    for k, word in enumerate(dictionary):
        inv_files[word] = set()
        for i, content in enumerate(lst_contents):
            if word in content:
                count = content.count(word)
                tf = count / len(content)
                tup_word_tf = (i, tf)
                inv_files[word].add(tup_word_tf)
    return inv_files


# Tính toán tf-idf
def calcu_word_tfidf(inv_files, lst_contents):
    tf_idf_arr = np.zeros(len(inv_files))
    total_content = len(lst_contents)
    for i, word in enumerate(inv_files):
        k = len(inv_files[word])
        idf = math.log(total_content / k)
        for tup in inv_files[word]:
            temp = list(tup)
            temp[1] *= idf
            tup = tuple(temp)
    return inv_files


# Xây dựng inverted file theo topic
def Build_invfile(a):
    contents, lst_contents, dictionary = Dic_building(a)
    inv_files = build_inverted_files(dictionary, lst_contents)
    inv_files = calcu_word_tfidf(inv_files, lst_contents)
    return contents, lst_contents, dictionary, inv_files


# Tính toán tfidf cho query
def Create_tfidf_query(query, lst_contents, inv_files):
    query_words = re.findall("(\w+)", query)
    dict_query = set()
    dict_query.update(query_words)
    dict_query = list(dict_query)
    tfidf_query = np.zeros(len(dict_query))
    total_content = len(lst_contents)
    for i, word in enumerate(dict_query):
        try:
            idf = 1 + np.log(total_content / len(inv_files[word]))
        except:
            idf = 1 + np.log(total_content)
        tfidf_query[i] = query_words.count(word) * idf / len(query_words)
    return tfidf_query, dict_query


# Thêm phần tử và kiểm tra
def Add_arr(arrs, arr):
    appear = False
    for i in arrs:
        if i[0] == arr[0]:
            appear = True
            break
    if appear == False:
        arrs.append(arr)
    else:
        for i in range(len(arrs)):
            if arrs[i][0] == arr[0]: arrs[i][1] += [1]
    return arrs


def swap(a, b):
    temp = a
    a = b
    b = temp
    return a, b


def Sort_arr(arr):
    for i in range(0, len(arr) - 1):
        for j in range(i + 1, len(arr)):
            if (arr[j][1] > arr[i][1]):
                arr[i][0], arr[j][0] = swap(arr[i][0], arr[j][0])
                arr[i][1], arr[j][1] = swap(arr[i][1], arr[j][1])
    return arr


# Mô hình tích vô hướng
def ScalarModel(tfidf_query, dict_query, inv_files, dic):
    # Tạo mảng chứa kết quả của tính vô hướng và sắp xếp
    kq_scalar = []
    for i, word in enumerate(dict_query):
        if word in dic:
            for tup in inv_files[word]:
                tempp = list(tup)
                tempp[1] = tempp[1] * tfidf_query[i]
                kq_scalar = Add_arr(kq_scalar, tempp)

    kq_scalar = Sort_arr(kq_scalar)
    arr_scalar = []
    for i in range(len(kq_scalar)):
        arr_scalar.append(kq_scalar[i][0])
    return arr_scalar


# Search
def Search(query, topic):
    contents, lst_contents, dic, inv_files = Build_invfile(topic)
    tfidf_query, dict_query = Create_tfidf_query(query, lst_contents, inv_files)
    scalar = ScalarModel(tfidf_query, dict_query, inv_files, dic)
    No = []
    for i in scalar:
        No.append(book_info._get_value(i, 'NO'))
    return No
