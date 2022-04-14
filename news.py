from pyasn1.type.univ import Null
import pymysql

from analysisData import PredictData

class news():
    def __init__(self, number):
        self.number = number
        self.title = Null
        self.time = Null
        self.content = Null
        self.happy = 0
        self.angry = 0
        self.hate = 0
        self.sad = 0
        self.positive = 0
        self.negative = 0
        self.male_num = 0  # 男性数量
        self.male_happy_num = 0  # 男性正面数量
        self.male_angry_num = 0  # 男性负面数量
        self.male_hate_num = 0  # 男性正面数量
        self.male_sad_num = 0  # 男性负面数量
        self.female_num = 0  # 女性数量
        self.female_happy_num = 0  # 男性正面数量
        self.female_angry_num = 0  # 男性负面数量
        self.female_hate_num = 0  # 男性正面数量
        self.female_sad_num = 0  # 男性负面数量
        self.area = []  # 地域信息
        self.hotIndex = 0  # 热度
        self.url = Null  # 微博链接
        self.alert = 0
        self.comment = [0 for i in range(10)]  # 评论内容
        self.count_like = [0 for i in range(10)]  # 评论对应的点赞数量
        self.comment_time = [0 for i in range(10)]  # 评论时间
        self.comment_emotion = [0 for i in range(10)]  # 评论对应的情绪

    def init(self, src, cur):
        # 除去news
        num = src[4:]
        cur.execute("select news_head,news_content,full_path,news_time from newsall where news_id=" + num)
        news_content = cur.fetchAll()
        self.title = news_content[0]  # 标题
        self.content = news_content[1]  # 内容
        self.url = news_content[2]  # 微博链接
        self.time = news_content[3]  # 新闻时间

        # 开始分析数据
        PredictData.predict(src, cur)

        index = titleAndIndex[1].split(',')
        self.happy = int(index[0])
        self.angry = int(index[1])
        self.hate = int(index[2])
        self.sad = int(index[3])
        self.male_num = int(index[4])
        self.male_happy_num = int(index[5])  # 男性正面数量
        self.male_angry_num = int(index[6])  # 男性负面数量
        self.male_hate_num = int(index[7])  # 男性正面数量
        self.male_sad_num = int(index[8])  # 男性负面数量
        self.female_num = int(index[9])  # 女性数量
        self.female_happy_num = int(index[10])  # 男性正面数量
        self.female_angry_num = int(index[11])  # 男性负面数量
        self.female_hate_num = int(index[12])  # 男性正面数量
        self.female_sad_num = int(index[13])  # 男性负面数量
        self.area.append(index[14].split('|')[0])  # 评论最多的地域1
        self.area.append(int(index[14].split('|')[1]))  # 评论最多的地域的评论数量1
        self.area.append(index[15].split('|')[0])  # 评论最多的地域2
        self.area.append(int(index[15].split('|')[1]))  # 评论最多的地域的评论数量2
        self.area.append(index[16].split('|')[0])  # 评论最多的地域2
        self.area.append(int(index[16].split('|')[1]))  # 评论最多的地域的评论数量2
        self.area.append(index[17].split('|')[0])  # 评论最多的地域2
        self.area.append(int(index[17].split('|')[1]))  # 评论最多的地域的评论数量2
        self.area.append(index[18].split('|')[0])  # 评论最多的地域2
        self.area.append(int(index[18].split('|')[1]))  # 评论最多的地域的评论数量2
        self.hotIndex = index[19].split('\n')[0]
        self.positive = self.happy
        self.negative = self.sad + self.hate + self.angry
        self.alert = int(self.hotIndex) * 30 / 5 + self.negative * 70 / (self.negative + self.positive)
        self.alert = round(self.alert, 1)


        for j in range(10):
            temp = f.readline()
            s = temp.split(';')
            self.comment[j] = s[3]
            self.count_like[j] = s[5].split('.')[0]
            self.comment_time[j] = s[4]
            self.comment_emotion[j] = s[0]
        # print(str(self.count_like[j]) + " " + str(self.comment_time[j]) + "" + str(self.comment_emotion[j]) + " " + str(self.comment[j]))
