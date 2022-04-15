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
        news_content = cur.fetchall()
        self.title = news_content[0][0]  # 标题
        self.content = news_content[0][1]  # 内容
        self.url = news_content[0][2]  # 微博链接
        self.time = news_content[0][3]  # 新闻时间
        print("标题" + str(self.title))
        print("内容" + str(self.content))
        print("微博链接" + str(self.url))
        print("新闻时间" + str(self.time))
        # 开始分析数据
        # PredictData.predict(src=src, cur=cur, news=self)

    # 从数据库里面直接读取信息
    def initialize(self, cur, num):
        cur.execute("select news_head,news_content,full_path,news_time from newsall where news_id=" + str(num))
        news_content = cur.fetchall()
        self.title = news_content[0][0]  # 标题
        self.content = news_content[0][1]  # 内容
        self.url = news_content[0][2]  # 微博链接
        self.time = news_content[0][3]  # 新闻时间

        info = cur.execute("select * from data where id = " + str(num))
        info = cur.fetchall()
        # print(info[0])
        # print(len(info[0]))
        # print(info[0][0])

        # index = titleAndIndex[1].split(',')
        self.happy = int(info[0][1])
        self.angry = int(info[0][2])
        self.hate = int(info[0][3])
        self.sad = int(info[0][4])
        self.male_num = int(info[0][5])
        self.male_happy_num = int(info[0][6])  # 男性正面数量
        self.male_angry_num = int(info[0][7])  # 男性负面数量
        self.male_hate_num = int(info[0][8])  # 男性正面数量
        self.male_sad_num = int(info[0][9])  # 男性负面数量
        self.female_num = int(info[0][10])  # 女性数量
        self.female_happy_num = int(info[0][11])  # 男性正面数量
        self.female_angry_num = int(info[0][12])  # 男性负面数量
        self.female_hate_num = int(info[0][13])  # 男性正面数量
        self.female_sad_num = int(info[0][14])  # 男性负面数量
        self.area.append(info[0][15])  # 评论最多的地域1
        self.area.append(int(info[0][16]))  # 评论最多的地域的评论数量1
        self.area.append(info[0][17])  # 评论最多的地域2
        self.area.append(int(info[0][18]))  # 评论最多的地域的评论数量2
        self.area.append(info[0][19])  # 评论最多的地域2
        self.area.append(int(info[0][20]))  # 评论最多的地域的评论数量2
        self.area.append(info[0][21])  # 评论最多的地域2
        self.area.append(int(info[0][22]))  # 评论最多的地域的评论数量2
        self.area.append(info[0][23])  # 评论最多的地域2
        self.area.append(int(info[0][24]))  # 评论最多的地域的评论数量2
        self.hotIndex = int(info[0][25])
        self.positive = self.happy
        self.negative = self.sad + self.hate + self.angry
        self.alert = int(self.hotIndex) * 30 / 5 + self.negative * 70 / (self.negative + self.positive)
        self.alert = round(self.alert, 1)

        info = cur.execute("select * from news" + str(num))
        info = cur.fetchall()
        for j in range(10):
            self.comment[j] = info[j][7]
            self.count_like[j] = info[j][9]
            self.comment_emotion[j] = '喜悦'
            # print(str(j)+" "+self.comment[j])
            # print(self.count_like)
            # print(self.comment_emotion)


