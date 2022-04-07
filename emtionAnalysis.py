#!/usr/bin/env python
# coding: utf-8

# In[29]:


import pandas as pd
path = 'F:\\emotionAnalyse\\simplifyweibo_4_moods\\'

pd_all = pd.read_csv(path + 'simplifyweibo_4_moods.csv')
moods = {0: '喜悦', 1: '愤怒', 2: '厌恶', 3: '低落'}

print('微博数目（总体）：%d' % pd_all.shape[0])

# for label, mood in moods.items(): 
#     print('微博数目（{}）：{}'.format(mood,  pd_all[pd_all.label==label].shape[0]))

print(pd_all.shape)


# In[30]:


li = pd_all.values
for i in range(100):
    print(li[i])


# In[31]:


n1 = 0
n2 = 0
n3 = 0
n4 = 0
newLines = ""
for line in li:
    label, sentence = line[0], line[1]
    if int(label) == 0:
        if n1 < 50000:
            n1 += 1
            newLines += str(label) + "\t" + sentence + "\n"
    if int(label) == 1:
        if n2 < 50000:
            n2 += 1
            newLines += str(label) + "\t" + sentence + "\n"
    if int(label) == 2:
        if n3 < 50000:
            n3 += 1
            newLines += str(label) + "\t" + sentence + "\n"
    if int(label) == 3:
        if n4 < 50000:
            n4 += 1
            newLines += str(label) + "\t" + sentence + "\n"
with open("F:\\emotionAnalyse\\small_train.txt", "w", encoding='UTF-8') as f2:
    f2.write(newLines)
    f2.close()


# In[1]:


# 数据清洗
import re

def cleanData(stringData):
    stringData = re.sub("[\s+\.\-\!\/_,$%^*()+\?\"\']+|[+——－；～【】：、“”‘’=……~@#￥%&*（）·]", "",stringData)
    return stringData


# In[2]:


# 加载停用词
def stopwords_list(file_path):
    stopwords = [line.strip() for line in open(file_path, 'r', encoding='utf-8').readlines()]
    return stopwords


# In[3]:


import collections
import jieba

word_freqs = collections.Counter()  # 词频
stopword = stopwords_list("F:\\emotionAnalyse\\stopWords.txt")
max_len = 0
with open('F:\\emotionAnalyse\\small_train.txt', 'r+', encoding="UTF-8",errors='ignore') as f:
    lines = f.readlines()
    for line in lines:
        # 取出label和句子
        label, sentence = line.strip("\n").split("\t")
        # 数据预处理
        sentence = cleanData(sentence)
        words = jieba.cut(sentence)
        x = 0
        for word in words:
            # 去除停用词
            if word not in stopword:
                word_freqs[word] += 1
                x += 1
        max_len = max(max_len, x)
print(max_len)
print('nb_words ', len(word_freqs))


# In[4]:


import pickle
MAX_FEATURES = 80000 # 最大词频数
vocab_size = min(MAX_FEATURES, len(word_freqs)) + 2
# 构建词频字典
word2index = {x[0]: i+2 for i, x in enumerate(word_freqs.most_common(MAX_FEATURES))}
word2index["PAD"] = 0
word2index["UNK"] = 1
# 将词频字典写入文件中保存
with open('F:\\emotionAnalyse\\word_dict.pickle', 'wb') as handle:
    pickle.dump(word2index, handle, protocol=pickle.HIGHEST_PROTOCOL)


# In[5]:


from keras.engine.saving import load_model
from keras.layers.core import Activation, Dense, SpatialDropout1D
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras.preprocessing import sequence
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import jieba
import numpy as np
import pandas as pd
import pickle


# In[6]:


# 加载分词字典
with open('F:\\emotionAnalyse\\word_dict.pickle', 'rb') as handle:
    word2index = pickle.load(handle)

### 准备数据
MAX_FEATURES = 80002 # 最大词频数
MAX_SENTENCE_LENGTH = 110 # 句子最大长度
num_recs = 0  # 样本数

with open('F:\\emotionAnalyse\\small_train.txt', 'r+', encoding="UTF-8",errors='ignore') as f:
    lines = f.readlines()
    # 统计样本大小
    for line in lines:
        num_recs += 1

# 初始化句子数组和label数组
X = np.empty(num_recs,dtype=list)
y = np.zeros(num_recs)
i=0


# In[7]:


with open('F:\\emotionAnalyse\\small_train.txt', 'r+', encoding="UTF-8",errors='ignore') as f:
    for line in f:
        label, sentence = line.strip("\n").split("\t")
        words = jieba.cut(sentence)
        seqs = []
        for word in words:
            # 在词频中
            if word in word2index:
                seqs.append(word2index[word])
            else:
                seqs.append(word2index["UNK"]) # 不在词频内的补为UNK
        X[i] = seqs
        y[i] = int(label)
        i += 1

# 把句子转换成数字序列，并对句子进行统一长度，长的截断，短的补0
X = sequence.pad_sequences(X, maxlen=MAX_SENTENCE_LENGTH)
# 使用pandas对label进行one-hot编码
y1 = pd.get_dummies(y).values
print(X.shape)
print(y1.shape)


# In[8]:


# 数据划分
Xtrain, Xtest, ytrain, ytest = train_test_split(X, y1, test_size=0.2, random_state=42)


# In[77]:


import matplotlib.pyplot as plt;
## 网络构建
EMBEDDING_SIZE = 256 # 词向量维度
HIDDEN_LAYER_SIZE = 128 # 隐藏层大小
BATCH_SIZE = 64 # 每批大小
NUM_EPOCHS = 10 # 训练周期数
# 创建一个实例
model = Sequential()
# 构建词向量
model.add(Embedding(MAX_FEATURES, EMBEDDING_SIZE,input_length=MAX_SENTENCE_LENGTH))
model.add(SpatialDropout1D(0.2))
# 构建LSTM层
model.add(LSTM(HIDDEN_LAYER_SIZE, dropout=0.2, recurrent_dropout=0.2))
# 输出层包含四个分类，激活函数设置为'softmax'
model.add(Dense(4, activation="softmax"))
model.add(Activation('softmax'))
# 损失函数设置为分类交叉熵categorical_crossentropy
model.compile(loss="categorical_crossentropy", optimizer="adam",metrics=["accuracy"])

## 训练模型
hist = model.fit(Xtrain, ytrain, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,validation_data=(Xtest, ytest))


# In[10]:


#画图
# loss：训练集损失值

# accuracy:训练集准确率

# val_loss:测试集损失值
    
# val_accruacy:测试集准确率
plt.plot(hist.history['loss'], label='loss')
plt.plot(hist.history['accuracy'], label='acc')
plt.plot(hist.history['val_loss'], label='val_loss')
plt.plot(hist.history['val_accuracy'], label='val_acc')
plt.legend()
plt.show()


# In[1]:


## 评估模型
y_pred = model.predict(Xtest)
y_pred = y_pred.argmax(axis=1)
ytest = ytest.argmax(axis=1)

print('accuracy %s' % accuracy_score(y_pred, ytest))
target_names = ['喜悦', '愤怒', '厌恶', '低落']
print(classification_report(ytest, y_pred, target_names=target_names))


# In[75]:


INPUT_SENTENCES = ['应该入刑！！孩子们是祖国的未来！']
XX = np.empty(len(INPUT_SENTENCES),dtype=list)
i=0
for sentence in  INPUT_SENTENCES:
    words = jieba.cut(sentence)
    seq = []
    for word in words:
        if word in word2index:
            seq.append(word2index[word])
        else:
            seq.append(word2index['UNK'])
    XX[i] = seq
    i+=1

XX = sequence.pad_sequences(XX, maxlen=MAX_SENTENCE_LENGTH)
label2word = {0:'喜悦', 1:'愤怒', 2:'厌恶', 3:'低落'}
for x in model.predict(XX):
    print(x)
    x = x.tolist()
    label = x.index(max(x[0], x[1], x[2], x[3]))
    print(label)
    print('{}'.format(label2word[label]))


# In[76]:


print("保存模型")

model.save('F:\\emotionAnalyse\\model\\emotionModel01.h5')

## 测试模型
# print("加载模型")
# model = load_model('model/my_model.h5')

