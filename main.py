from flask import Flask, render_template, request
from pyasn1.type.univ import Null
import pymysql
import random

from data import data
from news import news

app = Flask(__name__)

app.config['SECRET_KEY'] = '1456719640@qq.com'


@app.route("/")
def root():
    return render_template('Index.html', TitleAll=TitleAll, news=newsList[0], flag=1)


# 点击不同新闻按钮，刷新界面信息
@app.route("/refresh/<num>")
def refresh(num):
    news_choose = Null
    for i in range(len(newsList)):
        if str(newsList[i].number) == str(num):
            news_choose = newsList[i]
            break
    return render_template('Index.html', TitleAll=TitleAll, news=news_choose, flag=1)


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
        return render_template('Index.html', TitleAll=TitleAll, news=newsList[0], flag=-1)
    # 搜索成功
    else:
        return render_template('Index.html', TitleAll=TitleAll, news=news_choose1, flag=1)

# 连接数据库
def connectDB():
    conn = pymysql.connect(host='localhost', user="root", password="", database="weibo", charset='utf8')
    cursor = conn.cursor()
    return cursor


if __name__ == '__main__':
    # 进行数据训练
    # test = test()
    # test.predict()

    newsList = []
    cur = connectDB()
    newsSum = cur.execute("SELECT * FROM newsall")
    datanews = cur.fetchall()
    for i in range(5):
        num = random.randint(1, newsSum)
        srcTable = "news" + str(num)
        news1 = news(num)
        news1.init(srcTable, cur)
        newsList.append(news1)
    TitleAll = []
    for i in range(len(newsList)):
        TitleAll.append(newsList[i].title)

    app.run(debug=True, host='127.0.0.1', port='5000')
