from ..ch06_ECG import DS_detect
from ..ch06_ECG import readData
import numpy as np
import scipy.io as sio
# 截取全数据库目标心拍

def getHeart(PATH,HEADERFILE,ATRFILE,DATAFILE):
    SAMPLES2READ = 1800  # 指定需要读入的样本数
    # 若.dat文件中存储有两个通道的信号:则读入 2*SAMPLES2READ 个数据
    nosig, sfreq, dformat, gain, bitres, zerovalue, firstvalue = readData.read_hea(PATH, HEADERFILE)
    Time, M = readData.read_dat(PATH, DATAFILE, dformat, SAMPLES2READ, nosig, zerovalue, firstvalue, gain, sfreq)
    ANNOTD, ATRTIMED = readData.read_atr(PATH, ATRFILE, sfreq, Time, SAMPLES2READ)

    INFO = []
    Nb = []
    Lb = []
    Rb = []
    Vb = []
    Ab = []
    Sb = []
    Pl = 100
    Pr = 150

    # 调用QRS检测算法
    s = M[0]
    QRS_amp, QRS_ind = DS_detect.DS_detect(s, 0)
    Nt = len(QRS_ind)
    R_TIME = []
    ann = []
    for i in range(len(ATRTIMED)):
        if ANNOTD[i] in [1, 2, 3, 5, 8, 9]:
            R_TIME.append(ATRTIMED[i])
            ann.append(ANNOTD[i])
    REF_ind = []
    for i in range(len(R_TIME)):
        REF_ind.append(round(R_TIME[i] * 360))
    Nr = len(REF_ind)
    if Nt > Nr:
        typ = 0
    else:
        typ = 1
    if typ == 0:
        for i in range(Nr):
            ref = REF_ind[i]
            for m in range(Nt):
                act_ind = QRS_ind[m]
                if abs(ref - act_ind) <= 54:
                    if act_ind < Pl or (SAMPLES2READ - act_ind) < Pr:
                        break
                    else:
                        SEG = s[(act_ind - Pl):(act_ind + Pr)]
                    if ann[i] == 1:
                        if Nb == []:
                            Nb.extend(SEG)
                        else:
                            Nb = np.vstack((Nb, SEG))
                    elif ann[i] == 2:
                        if Lb == []:
                            Lb.extend(SEG)
                        else:
                            Lb = np.vstack((Lb, SEG))
                    elif ann[i] == 3:
                        if Rb == []:
                            Rb.extend(SEG)
                        else:
                            Rb = np.vstack((Rb, SEG))
                    elif ann[i] == 5:
                        if Vb == []:
                            Vb.extend(SEG)
                        else:
                            Vb = np.vstack((Vb, SEG))
                    elif ann[i] == 8:
                        if Ab == []:
                            Ab.extend(SEG)
                        else:
                            Ab = np.vstack((Ab, SEG))
                    elif ann[i] == 9:
                        if Sb == []:
                            Sb.extend(SEG)
                        else:
                            Sb = np.vstack((Sb, SEG))
                    break
    else:
        for i in range(Nt):
            act_ind = QRS_ind[i]
            for m in range(Nr):
                if abs(act_ind - REF_ind[m]) <= 54:
                    if act_ind < Pl or (SAMPLES2READ - act_ind) < Pr:
                        break
                    else:
                        SEG = s[(act_ind - Pl):(act_ind + Pr)]
                    if ann[i] == 1:
                        if Nb == []:
                            Nb.extend(SEG)
                        else:
                            Nb = np.vstack((Nb, SEG))
                    elif ann[i] == 2:
                        if Lb == []:
                            Lb.extend(SEG)
                        else:
                            Lb = np.vstack((Lb, SEG))
                    elif ann[i] == 3:
                        if Rb == []:
                            Rb.extend(SEG)
                        else:
                            Rb = np.vstack((Rb, SEG))
                    elif ann[i] == 5:
                        if Vb == []:
                            Vb.extend(SEG)
                        else:
                            Vb = np.vstack((Vb, SEG))
                    elif ann[i] == 8:
                        if Ab == []:
                            Ab.extend(SEG)
                        else:
                            Ab = np.vstack((Ab, SEG))
                    elif ann[i] == 9:
                        if Sb == []:
                            Sb.extend(SEG)
                        else:
                            Sb = np.vstack((Sb, SEG))
                    break
    return Nb

if __name__ == '__main__':
    PATH = 'D:\Program Files\RatternRecognition\database\MIT-BIH\\'  # 指定数据的储存路径
    HEADERFILE = '100.hea'  # .hea 格式，头文件，可用记事本打开
    ATRFILE = '100.atr'  # .atr 格式，属性文件，数据格式为二进制数
    DATAFILE = '100.dat'  # .dat 格式，ECG 数据
    heart = getHeart(PATH,HEADERFILE,ATRFILE,DATAFILE)
    # sio.savemat('Feature',{'feature':Nb})