from keras.models import load_model
from keras.preprocessing import sequence
import pickle
import numpy as np
import jieba
import random
from pyasn1.type.univ import Null


class PredictData:
    def __init__(self):
        print("加载模型")
        self.happy = 0
        self.angry = 0
        self.hate = 0
        self.sad = 0
        self.commentText = Null  # 评论信息
        self.createTime = Null  # 评论时间
        self.likeCount = 0  # 点赞量
        self.sex_male = 0  # 男性评论者数量
        self.sex_male_happy = 0  # 男性评论者中，正面情绪的数量
        self.sex_male_angry = 0  # 男性评论者中，负面情绪的数量
        self.sex_male_hate = 0  # 男性评论者中，负面情绪的数量
        self.sex_male_sad = 0  # 男性评论者中，负面情绪的数量
        self.sex_female = 0  # 女性评论者数量
        self.sex_female_happy = 0  # 男性评论者中，正面情绪的数量
        self.sex_female_angry = 0  # 男性评论者中，负面情绪的数量
        self.sex_female_hate = 0  # 男性评论者中，负面情绪的数量
        self.sex_female_sad = 0  # 男性评论者中，负面情绪的数量
        self.province_num = [0 for i in range(35)]
        self.emog_happy = ['😁', '😃', '😄', '😉', '🤗', '😘', '😋', '😎', '😆', '😊']
        self.emog_angry = ['😖', '😤', '😕', '😓', '😡', '😈', '💩', '😠', '😩', '😤']
        self.emog_hate = ['😖', '😤', '😕', '😓', '🙁', '😖', '💩', '😩', '😧', '😴']
        self.emog_sad = ['😢', '😭', '😩', '😓', '😞', '😱', '😨', '😩', '😷', '🤧']
        self.model = load_model('./model/emotionModel01.h5')  # 加载模型
        with open('./word_dict.pickle', 'rb') as handle:  # 加载分词字典
            self.word2index = pickle.load(handle)

    def predictPartOfNews(self, news):
        AllCommentText = news.comment
        i = 0
        XX = np.empty(len(AllCommentText), dtype=list)
        for sentence in AllCommentText:
            if len(sentence) == 0:
                continue
            sentence  # 待预测的评论
            words = jieba.cut(sentence)
            seq = []
            for word in words:
                if word in self.word2index:
                    seq.append(self.word2index[word])
                else:
                    seq.append(self.word2index['UNK'])
            XX[i] = seq
            i += 1
        MAX_SENTENCE_LENGTH = 110  # 句子最大长度
        XX = sequence.pad_sequences(XX, maxlen=MAX_SENTENCE_LENGTH)
        label2word = {0: '喜悦', 1: '愤怒', 2: '厌恶', 3: '低落'}
        YY = self.model.predict(XX)
        j = 0
        for x in YY:
            x = x.tolist()
            label = x.index(max(x[0], x[1], x[2], x[3]))
            news.comment_emotion[j] = label2word[label]

            temp = random.random()  # 生成一个0-1之间的随机数
            temp2 = random.randint(0,9)

            if label == 0:
                if temp < 0.3:
                    news.comment[j] = news.comment[j] + self.emog_happy[temp2]
                    if temp < 0.1:
                        news.comment[j] = news.comment[j] + self.emog_happy[temp2]
            if label == 1:
                if temp < 0.2:
                    news.comment[j] = news.comment[j] + self.emog_angry[temp2]
                    if temp < 0.05:
                        news.comment[j] = news.comment[j] + self.emog_angry[temp2]
            if label == 2:
                if temp < 0.3:
                    news.comment[j] = news.comment[j] + self.emog_hate[temp2]
            if label == 3:
                if temp < 0.5:
                    news.comment[j] = news.comment[j] + self.emog_sad[temp2]
                    if temp < 0.1:
                        news.comment[j] = news.comment[j] + self.emog_sad[temp2]
            j += 1

    def predict(self, src, cur, news):

        # 评论总数
        comment_sum = cur.execute("select comment_text,create_time,like_count,commentor_sex,commentor_addr from " + src)
        # 所有评论信息
        comments = cur.fetchall()
        comments = list(comments)
        for i in range(len(comments)):
            comments[i] = list(comments[i])

        all_comment_text = []
        all_create_time = []
        all_like_count = []
        all_sex = []
        all_province = []
        for elem in comments:
            all_comment_text.append(elem[0])  # 获取评论所有内容
            all_create_time.append(elem[1])  # 获取所有的评论时间
            all_like_count.append(elem[2])  # 获取所有的点赞量
            all_sex.append(elem[3])  # 获取所有的性别
            all_province.append(elem[4])  # 获取所有的评论者所在地

        for j in range(1, len(all_comment_text)):
            if len(all_comment_text[j]) == 0:
                continue
            self.changeProvince(all_province[0])
            # INPUT_SENTENCES = [all_comment_text]  # 待预测的评论
            XX = np.empty(len(all_comment_text[j]), dtype=list)
            i = 0
            for sentence in all_comment_text[j]:
                words = jieba.lcut(sentence)
                seq = []
                if len(words) == 0:
                    continue
                for word in words:
                    if word in self.word2index:
                        seq.append(self.word2index[word])
                    else:
                        seq.append(self.word2index['UNK'])
                XX[i] = seq
                i += 1
            MAX_SENTENCE_LENGTH = 110  # 句子最大长度

            XX = sequence.pad_sequences(XX, maxlen=MAX_SENTENCE_LENGTH)
            # print(len(XX))
            label2word = {0: '喜悦', 1: '愤怒', 2: '厌恶', 3: '低落'}
            X = self.model.predict(XX)
            for x in X:
                x = x.tolist()
                label = x.index(max(x[0], x[1], x[2], x[3]))
                # 统计情绪数量
                if label == 0:
                    self.happy = self.happy + 1
                if label == 1:
                    self.angry = self.angry + 1
                if label == 2:
                    self.hate = self.hate + 1
                if label == 3:
                    self.sad = self.sad + 1
                # 统计性别和情绪的信息
                if all_sex[j] == "女":
                    self.sex_female = self.sex_female + 1
                    # 女性评论者中，正面情绪的数量
                    if label == 0:
                        self.sex_female_happy = self.sex_female_happy + 1
                    # 女性评论者中，负面情绪的数量
                    elif label == 1:
                        self.sex_female_angry = self.sex_female_angry + 1
                    elif label == 2:
                        self.sex_female_hate = self.sex_female_hate + 1
                    else:
                        self.sex_female_sad = self.sex_female_sad + 1
                else:
                    self.sex_male = self.sex_male + 1
                    if label == 0:
                        self.sex_male_happy = self.sex_male_happy + 1
                    elif label == 1:
                        self.sex_male_angry = self.sex_male_angry + 1
                    elif label == 2:
                        self.sex_male_hate = self.sex_male_hate + 1
                    else:
                        self.sex_male_sad = self.sex_male_sad + 1

                print(label)  # 输出0，喜悦的标签编号
                # print('{}'.format(label2word[label]))   #输出汉字“喜悦"
                result = str('{}'.format(label2word[label])) + ";" + str(label) + ";" + str(x) + ";" + str(
                    all_comment_text[j]) + ";" + str(all_create_time[j]) + ";" + str(all_like_count[j]) + "\n"
                # print(result)
            # f.write(result)  # 自带文件关闭功能，不需要再写f.close()
        fiveMostProvince = self.chooseFiveMostProvince(news)
        print("#################五个评论最多的身份:" + str(fiveMostProvince))
        print(str(self.happy) + "," + str(self.angry) + "," + str(self.hate) + "," + str(self.sad) + "," + str(
            self.sex_male) + "," + str(self.sex_male_happy) + "," + str(self.sex_male_angry) + "," + str(
            self.sex_male_hate) + "," + str(self.sex_male_sad) + "," + str(
            self.sex_female) + "," + str(self.sex_female_happy) + "," + str(self.sex_female_angry) + "," + str(
            self.sex_female_hate) + "," + str(self.sex_female_sad) + "," + fiveMostProvince)
        news.happy = self.happy
        news.angry = self.angry
        news.hate = self.hate
        news.sad = self.sad
        news.male_num = self.sex_male
        news.male_happy_num = self.sex_male_happy
        news.male_angry_num = self.sex_male_angry
        news.male_hate_num = self.sex_male_hate
        news.male_sad_num = self.sex_male_sad
        news.female_num = self.sex_female
        news.female_happy_num = self.sex_female_happy
        news.female_angry_num = self.sex_female_angry
        news.female_hate_num = self.sex_female_hate
        news.female_sad_num = self.sex_female_sad
        self.justify()

    def justify(self):
        self.happy = 0
        self.angry = 0
        self.hate = 0
        self.sad = 0
        self.commentText = Null  # 评论信息
        self.createTime = Null  # 评论时间
        self.likeCount = 0  # 点赞量
        self.sex_male = 0  # 男性评论者数量
        self.sex_male_happy = 0  # 男性评论者中，正面情绪的数量
        self.sex_male_angry = 0  # 男性评论者中，负面情绪的数量
        self.sex_male_hate = 0  # 男性评论者中，负面情绪的数量
        self.sex_male_sad = 0  # 男性评论者中，负面情绪的数量
        self.sex_female = 0  # 女性评论者数量
        self.sex_female_happy = 0  # 男性评论者中，正面情绪的数量
        self.sex_female_angry = 0  # 男性评论者中，负面情绪的数量
        self.sex_female_hate = 0  # 男性评论者中，负面情绪的数量
        self.sex_female_sad = 0  # 男性评论者中，负面情绪的数量
        for i in range(len(self.province_num)):
            self.province_num[i] = 0

    # 挑选五个评论者最多的省份
    def chooseFiveMostProvince(self, news):
        maxFive = ""
        max_value = 0  # 此论最大值
        max_value_index = 0  # 此轮最大值所在的列表下标
        max_value_pro = ""  # 此论最大值对应的省份
        for j in range(5):
            for i in range(1, len(self.province_num)):
                if max_value < self.province_num[i]:
                    max_value = self.province_num[i]
                    max_value_index = i
            # 找到max_value_index对应的省份
            max_value_pro = self.findprovince(max_value_index)
            # 将此轮最大值添加到maxFive中
            news.area.append(str(max_value_pro));
            news.area.append(str(max_value));
            # maxFive = str(maxFive) + str(max_value_pro) + "|" + str(max_value) + ","
            # 将此轮最大值置为0
            self.province_num[max_value_index] = 0
            max_value = 0  # 下一轮最大值
            max_value_index = 0  # 下一轮最大值所在的列表下标
            max_value_pro = ""  # 下一轮最大值对应的省份
        return maxFive

    def findprovince(self, index):
        if index == 1:
            return "台湾"
        if index == 2:
            return "广东"
        if index == 3:
            return "江苏"
        if index == 4:
            return "浙江"
        if index == 5:
            return "山东"
        if index == 6:
            return "福建"
        if index == 7:
            return "辽宁"
        if index == 8:
            return "黑龙江"
        if index == 9:
            return "河北"
        if index == 10:
            return "湖北"
        if index == 11:
            return "湖南"
        if index == 12:
            return "安徽"
        if index == 13:
            return "吉林"
        if index == 14:
            return "海南"
        if index == 15:
            return "四川"
        if index == 16:
            return "陕西"
        if index == 17:
            return "山西"
        if index == 18:
            return "河南"
        if index == 19:
            return "新疆"
        if index == 20:
            return "江西"
        if index == 21:
            return "广西"
        if index == 22:
            return "内蒙古"
        if index == 23:
            return "云南"
        if index == 24:
            return "甘肃"
        if index == 25:
            return "宁夏"
        if index == 26:
            return "青海"
        if index == 27:
            return "贵州"
        if index == 28:
            return "西藏"
        if index == 29:
            return "北京"
        if index == 30:
            return "上海"
        if index == 31:
            return "天津"
        if index == 32:
            return "重庆"
        if index == 33:
            return "香港"
        if index == 34:
            return "澳门"

    # 设置评论者省份信息
    def changeProvince(self, province):
        """1.台湾省 2.广东省 3.江苏省 4.浙江省 5.山东省 6.福建省 7.辽宁省
            8.黑龙江省 9.河北省 10.湖北省 11.湖南省 12.安徽省 13.吉林省 14.海南省
            15.四川省 16.陕西省 17.山西省 18.河南省 19.新疆区 20.江西省 21.广西区
            22.内蒙古区 23.云南省 24.甘肃省 25.宁夏区 26.青海省 27.贵州省 28.西藏区 29.北京
            30.上海 31.天津 32.重庆 33.香港 34.澳门"""
        if province != Null:
            province = province.split(' ')[0]
            if province == "台湾":
                self.province_num[1] = self.province_num[1] + 1
            if province == "广东":
                self.province_num[2] = self.province_num[2] + 1
            if province == "江苏":
                self.province_num[3] = self.province_num[3] + 1
            if province == "浙江":
                self.province_num[4] = self.province_num[4] + 1
            if province == "山东":
                self.province_num[5] = self.province_num[5] + 1
            if province == "福建":
                self.province_num[6] = self.province_num[6] + 1
            if province == "辽宁":
                self.province_num[7] = self.province_num[7] + 1
            if province == "黑龙江":
                self.province_num[8] = self.province_num[8] + 1
            if province == "河北":
                self.province_num[9] = self.province_num[9] + 1
            if province == "湖北":
                self.province_num[10] = self.province_num[10] + 1
            if province == "湖南":
                self.province_num[11] = self.province_num[11] + 1
            if province == "安徽":
                self.province_num[12] = self.province_num[12] + 1
            if province == "吉林":
                self.province_num[13] = self.province_num[13] + 1
            if province == "海南":
                self.province_num[14] = self.province_num[14] + 1
            if province == "四川":
                self.province_num[15] = self.province_num[15] + 1
            if province == "陕西":
                self.province_num[16] = self.province_num[16] + 1
            if province == "山西":
                self.province_num[17] = self.province_num[17] + 1
            if province == "河南":
                self.province_num[18] = self.province_num[18] + 1
            if province == "新疆":
                self.province_num[19] = self.province_num[19] + 1
            if province == "江西":
                self.province_num[20] = self.province_num[20] + 1
            if province == "广西":
                self.province_num[21] = self.province_num[21] + 1
            if province == "内蒙古":
                self.province_num[22] = self.province_num[22] + 1
            if province == "云南":
                self.province_num[23] = self.province_num[23] + 1
            if province == "甘肃":
                self.province_num[24] = self.province_num[24] + 1
            if province == "宁夏":
                self.province_num[25] = self.province_num[25] + 1
            if province == "青海":
                self.province_num[26] = self.province_num[26] + 1
            if province == "贵州":
                self.province_num[27] = self.province_num[27] + 1
            if province == "西藏":
                self.province_num[28] = self.province_num[28] + 1
            if province == "北京":
                self.province_num[29] = self.province_num[29] + 1
            if province == "上海":
                self.province_num[30] = self.province_num[30] + 1
            if province == "天津":
                self.province_num[31] = self.province_num[31] + 1
            if province == "重庆":
                self.province_num[32] = self.province_num[32] + 1
            if province == "香港":
                self.province_num[33] = self.province_num[33] + 1
            if province == "澳门":
                self.province_num[34] = self.province_num[34] + 1

    def predictold(self):
        INPUT_SENTENCES = ['今天好开心呀！', '很生气', '我很开心']
        XX = np.empty(len(INPUT_SENTENCES), dtype=list)
        i = 0
        for sentence in INPUT_SENTENCES:
            words = jieba.cut(sentence)
            seq = []
            for word in words:
                if word in self.word2index:
                    seq.append(self.word2index[word])
                else:
                    seq.append(self.word2index['UNK'])
            XX[i] = seq
            i += 1

        MAX_SENTENCE_LENGTH = 110  # 句子最大长度
        XX = sequence.pad_sequences(XX, maxlen=MAX_SENTENCE_LENGTH)
        label2word = {0: '喜悦', 1: '愤怒', 2: '厌恶', 3: '低落'}
        print(XX)
        for x in self.model.predict(XX):
            # print(x)
            x = x.tolist()
            print(x)
            label = x.index(max(x[0], x[1], x[2], x[3]))
            print(label)
            print('{}'.format(label2word[label]))
