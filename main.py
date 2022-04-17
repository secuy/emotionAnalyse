from flask import Flask, render_template, request
from pyasn1.type.univ import Null
import pymysql
import random
from keras.models import load_model
import pickle

from analysisData import PredictData
from news import news

app = Flask(__name__)

app.config['SECRET_KEY'] = '1456719640@qq.com'

newsList = []
TitleAll = []

@app.route("/")
def root():
    global newsList
    global TitleAll
    newsList = []
    TitleAll = []
    chooseNews(newsList, TitleAll)
    return render_template('index.html', TitleAll=TitleAll, news=newsList[0], flag=1)


# 点击不同新闻按钮，刷新界面信息
@app.route("/refresh/<num>")
def refresh(num):
    news_choose = newsList[int(num)]
    return render_template('index.html', TitleAll=TitleAll, news=news_choose, flag=1)


# 点击搜索框
@app.route("/search", methods=['GET', 'POST'])
def search():
    news_choose1 = Null
    searchContent = request.args.get('search1')
    p = 0
    for j in range(len(newsList)):
        if searchContent in newsList[j].title:
            news_choose1 = newsList[j]
            p = 1
            print(news_choose1.title + "&&&&&&& " + str(j) + " 已经改变了")
            break
    # 搜索失败
    if p == 0:
        return render_template('index.html', TitleAll=TitleAll, news=newsList[0], flag=-1)
    # 搜索成功
    else:
        return render_template('index.html', TitleAll=TitleAll, news=news_choose1, flag=1)


# 连接数据库
def connectDB():
    # 这里的user和passwd在上传服务器的时候要更改
    conn = pymysql.connect(host='localhost', user="root", password="", database="weibo", charset='utf8')
    cursor = conn.cursor()
    return cursor


def chooseNews(newsList, TitleAll):
    Predic = PredictData(model, word_dic)

    temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    newsSum = cur.execute("SELECT * FROM newsall")
    datanews = cur.fetchall()
    nums = random.sample(range(1, newsSum + 1), 5)
    for num in nums:
        temp[num - 1] = 1
        srcTable = "news" + str(num)
        news1 = news(num)
        news1.initialize(cur, num)
        Predic.predictPartOfNews(news1)
        newsList.append(news1)

    # 查看还有哪些新闻没被读入
    for i in range(len(temp)):
        # 若temp[i] ==0 说明，新闻（i+1）还没被读入，则读入新闻（i+1）
        if temp[i] == 0:
            srcTable = "news" + str(i + 1)
            news2 = news(i + 1)
            news2.initialize(cur, i + 1)
            Predic.predictPartOfNews(news2)
            newsList.append(news2)
            temp[i] = 1

    # 在titleAll中加入所有的新闻标题

    for i in range(len(newsList)):
        TitleAll.append(newsList[i].title)

if __name__ == '__main__':
    cur = connectDB()
    model = load_model('./model/emotionModel01.h5')  # 加载模型
    with open('./word_dict.pickle', 'rb') as handle:  # 加载分词字典
        word_dic = pickle.load(handle)
    app.run(debug=True, host='0.0.0.0', port=8080)
    # 0.0.0.0用于外网访问
