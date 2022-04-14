import os

import numpy as np
class data():
    def __init__(self, a, list):
        self.data = a
        self.dictionary = list

    #       for i in range(len(self.data)):
    #          for j in range(len(self.data[i])):
    #              print(self.data[i][j])

    def readDataFromTxt(self):
        for i in range(3):
            #src = "D:/我的文件们/6大三下/计算机设计大赛/评论数据/" + str(i+1) + ".txt"
            src = os.path.join(os.path.dirname(__file__) + "\\commentData\\" + str(i + 1) + ".txt")
            j = 0
            with open(src, "r", encoding='UTF-8') as f:  # 打开文件
                dataread = f.readline()  # 读取文件
                while dataread:
                    if(dataread != ''):
                        self.data[i+1][j] = dataread
                        j = j+1
                        dataread = f.readline()
                       # print(str(i)+" "+str(j)+" "+str(self.data[i][j]))
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                self.dictionary[i][j] = str(i)+str(j)
        self.data = np.array(self.data).flatten()
        self.dictionary = np.array(self.dictionary).flatten()
        self.dictionary = dict(zip(self.dictionary, self.data))

