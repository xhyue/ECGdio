from ..ch06_ECG import segBeat
from ..ch06_ECG import readData
import pywt
import numpy as np
from sklearn.externals import joblib



def getResult(PATH,HEADERFILE,ATRFILE,DATAFILE):
    # 数据读取与显示
    SAMPLES2READ = 1800  # 指定需要读入的样本数
    # 若.dat文件中存储有两个通道的信号:则读入 2*SAMPLES2READ 个数据
    nosig, sfreq, dformat, gain, bitres, zerovalue, firstvalue = readData.read_hea(PATH, HEADERFILE)
    Time, M = readData.read_dat(PATH, DATAFILE, dformat, SAMPLES2READ, nosig, zerovalue, firstvalue, gain, sfreq)
    ANNOTD, ATRTIMED = readData.read_atr(PATH, ATRFILE, sfreq, Time, SAMPLES2READ)

    # 截取拍心位置
    heart = segBeat.getHeart(PATH, HEADERFILE, ATRFILE, DATAFILE)

    # 获取小波特征
    data = heart[0]
    # 使信号的均值为0，去掉基线的影响
    a = np.mean(data)
    data = data - np.mean(data)
    # db6小波5级分解
    features = pywt.wavedec(data, 'db6', level=5)
    feature = []
    for i in range(len(features)):
        feature = np.hstack((feature, features[i]))
    feature = feature.reshape((1, len(feature)))

    # 类别预测
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    clf = joblib.load(BASE_DIR+"/svm_model.m")
    y_pred = clf.predict(feature[:, :25])

    dict = {'1.0': '正常脉搏',
            '2.0': '左束支传导阻滞',
            '3.0': '右束支传导阻滞',
            '4.0': '异常房室早搏',
            }
    heart_type = dict.get(str(y_pred[0]))
    return Time,M,heart_type

def exec_create_img(headerfile, atrfile, datafile, patname):
    PATH = ''  # 指定数据的储存路径
    HEADERFILE = str(headerfile)  # .hea 格式，头文件，可用记事本打开
    ATRFILE = str(atrfile)  # .atr 格式，属性文件，数据格式为二进制数
    DATAFILE = str(datafile)  # .dat 格式，ECG 数据
    Time, M,heart_type = getResult(PATH,HEADERFILE,ATRFILE,DATAFILE)
    # 显示
    readData.display_data(Time, M, patname)
    return heart_type

