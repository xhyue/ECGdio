import numpy as np
import scipy.io as sio
from scipy import signal
import pandas as pd
import matplotlib.pyplot as plt

# 输入
# % ecg_i : 原信号，一维向量
# % gr : 绘图与否，0：不绘图，1：绘图
#  输出
# % QRS_amp:QRS波振幅.
# % QRS_ind:QRS波索引.
# % 绘制图像.
def DS_detect(ecg_i,gr):
    fs = 360
    s = ecg_i
    N = len(s)
    ECG = s
    # 使用fdatool设计并导出的滤波器系数,带通FIR,15~25Hz,详情使用fdatool打开DS1.fda查看
    FIR_c1 = [0.0041, 0.0053, 0.0068, 0.0080, 0.0081, 0.0058, -0.0000, -0.0097, -0.0226,
              - 0.0370, -0.0498, -0.0577, -0.0576, -0.0477, -0.0278, 0, 0.0318, 0.0625, 0.0867,
              0.1000, 0.1000, 0.0867, 0.0625, 0.0318, 0, -0.0278, -0.0477, -0.0576, -0.0577,
              - 0.0498, -0.0370, -0.0226, -0.0097, -0.0000, 0.0058, 0.0081, 0.0080, 0.0068,
              0.0053, 0.0041]
    # 使用fdatool设计并导出的滤波器系数,低通FIR,截止频率5Hz,详情使用fdatool打开DS2.fda查看
    FIR_c2 = [0.0070, 0.0094, 0.0162, 0.0269, 0.0405, 0.0555, 0.0703, 0.0833, 0.0928,
              0.0979, 0.0979, 0.0928, 0.0833, 0.0703, 0.0555, 0.0405, 0.0269, 0.0162, 0.0094,
              0.0070]
    l1 = len(FIR_c1)
    head = list(np.ones(l1)*ECG[0])
    tail = list(np.ones(l1)*ECG[N-1])
    # 数据点延拓，防止滤波边缘效应
    ECG_1 = []
    ECG_1.extend(head)
    ECG_1.extend(ECG)
    ECG_1.extend(tail)
    # 带通滤波
    ECG = signal.filtfilt(FIR_c1,1,ECG_1)
    # 前面延拓了数据点，这里截取有用的部分
    ECG = ECG[l1:(N+l1)]
    # 双斜率处理
    # 两侧目标区间0.015~0.060s
    a = round(0.015*fs)
    b = round(0.06*fs)
    # 确保在不超过信号长度
    Ns = N-2*b
    S_l = np.zeros(b-a+1)
    S_r = np.zeros(b-a+1)
    S_dmax = np.zeros(Ns)
    # 对每个点双斜率处理
    for i in range(Ns):
        for j in range(a,b):
            S_l[j - a] = (ECG[i + b] - ECG[i + b - j]) / j
            S_r[j - a] = (ECG[i + b] - ECG[i + b + j]) / j
        S_lmax = S_l.max()
        S_lmin = S_l.min()
        S_rmax = S_r.max()
        S_rmin = S_r.min()
        C1 = S_rmax - S_lmin
        C2 = S_lmax - S_rmin
        S_dmax[i] = max(C1,C2)

    # 再次进行低通滤波，思路与上述带通滤波一致
    l2 = len(FIR_c2)
    head = list(np.ones(l2) *S_dmax[0])
    tail = list(np.ones(l1) * S_dmax[Ns-1])
    # 数据点延拓，防止滤波边缘效应
    S_dmaxl = []
    S_dmaxl.extend(head)
    S_dmaxl.extend(S_dmax)
    S_dmaxl.extend(tail)
    # 低通滤波
    S_dmaxt = signal.filtfilt(FIR_c2, 1, S_dmaxl)
    # 前面延拓了数据点，这里截取有用的部分
    S_dmaxt = S_dmaxt[l2:(Ns + l2)]

    # 滑动窗口积分
    w = 8
    wd = 7
    d_1 = []
    # 零延拓，确保所有的点都可以进行窗口积分
    d_1.extend(list(np.zeros(w)))
    d_1.extend(S_dmaxt)
    d_1.extend(list(np.zeros(w)))
    m = list(np.zeros(Ns))
    for i in range(w+1,Ns+w):
        m[i-w] = sum(d_1[i-w:i+w])
    m_l = []
    m_l.extend(list(np.zeros(wd)*m[0]))
    m_l.extend(m)
    m_l.extend(list(np.zeros(wd)*m[Ns-1]))

    # 双阈值检测与动态变化
    # 存储检测到的QRS波索引
    QRS_buf1 = []
    # 存储最近检测到的8个QRS波对应特征信号的波峰值
    AMP_buf1 = []
    thr_init0 = 0.4
    thr_lim0 = 0.23
    # 阈值变化的初始值和下限设置
    thr_init1 = 0.6
    thr_lim1 = 0.3
    # 标记波峰检出情况，高于高阈值--1，高低阈值之间--0，未检出-- -1
    en = -1
    thr0 = thr_init0
    thr1 = thr_init1
    # 阈值缓存，记录阈值变化情况
    thr1_buf = []
    thr0_buf = []
    for j in range(8,Ns):
        t = 1
        cri = 1
        # 检测候选波峰
        while t<=wd and cri>0 :
            cri = ((m_l[j] - m_l[j - t]) > 0) and ((m_l[j] - m_l[j + t]) > 0)
            t = t + 1
        if t ==wd+1 :
            # N1: 已经检测到的QRS波个数
            N1 = len(QRS_buf1)
            # 高于高阈值时的处理
            if m_l[j] > thr1 :
                # N1小于2时直接存储
                if N1 < 2 :
                    # j-wd 减去了滑动窗口积分带来的延迟
                    QRS_buf1.append(j-wd)
                    AMP_buf1.append(m_l[j])
                    en = 1
                else:
                    dist = j-wd-QRS_buf1[N1-1]
                    # 检测波峰距离
                    if dist>0.24*fs:
                        QRS_buf1.append(j - wd)
                        AMP_buf1.append(m_l[j])
                        en = 1
                    else:
                        # 不应期处理
                        if m_l[j]>AMP_buf1[len(AMP_buf1)-1]:
                            QRS_buf1[len(QRS_buf1)-1] = j-wd
                            AMP_buf1[len(AMP_buf1) - 1] = m_l[j]
                            en = 1
            # 特征峰值低于高阈值
            else:
                # 特征峰值在两阈值之间
                if N1<2 and m_l[j]>thr0:
                    QRS_buf1.append(j - wd)
                    AMP_buf1.append(m_l[j])
                    en = 0
                else:
                    # 特征峰值在两阈值之间
                    if m_l[j]>thr0:
                        temp = pd.DataFrame(QRS_buf1).diff(axis=1).dropna()
                        dist_m =np.array(temp).mean()
                        dist = j - wd - QRS_buf1[N1]
                        # 不应期检测，并且，波峰要距离足够远（> 平均距离的一半）
                        if dist>0.24*fs and dist>0.5*dist_m :
                            QRS_buf1.append(j - wd)
                            AMP_buf1.append(m_l[j])
                            en = 0
                        else:
                            if m_l[j] > AMP_buf1[len(AMP_buf1) - 1]:
                                QRS_buf1[len(QRS_buf1) - 1] = j - wd
                                AMP_buf1[len(AMP_buf1) - 1] = m_l[j]
                                en = 0
                    else:
                        en = -1
            N2 = len(AMP_buf1)
            if N2>8:
                # 确保只存储最近的8个特征波峰
                AMP_buf1 = AMP_buf1[2:9]
            # 下面的if与博文中的公式对应
            if en == 1:
                thr1 = 0.7*np.array(AMP_buf1).mean()
                thr0 = 0.25*np.array(AMP_buf1).mean()
            elif en == 0:
                temp = abs(m_l[j]-np.array(AMP_buf1).mean())
                thr1 = thr1-temp/2
        # 确保阈值高于下限
        if thr1 <= thr_lim1:
            thr1 = thr_lim1
        if thr0 <= thr_lim0:
            thr0 = thr_lim0
        thr0_buf.append(thr0)
        thr1_buf.append(thr1)
    delay = round(l1/2)-2*w+2
    # 减去延迟，得到最终结果
    QRS_ind = []
    QRS_amp =[]
    for i in range(len(QRS_buf1)):
        # QRS_ind.append(int(QRS_buf1[i] - delay))
        QRS_ind.append(int(QRS_buf1[i] - delay+29))
        QRS_amp.append(s[int(QRS_buf1[i] - delay+29)])

    # 绘图
    if gr == 1:
        plt.figure(1)
        plt.subplot(211)
        plt.plot(m,label='Feature Signal')
        plt.axis([1,len(m),-0.3,1.6*max(m)])
        plt.title('Feature signal and thresholds')
        points = []
        for i in range(len(QRS_buf1)):
            points.append(m[int(QRS_buf1[i])])
        plt.plot(QRS_buf1,points,'ro',label='QRS Locations')
        plt.plot(thr1_buf,'r',label='Threshold1')
        plt.plot(thr0_buf, 'r', label='Threshold0')
        plt.subplot(212)
        plt.plot(s,label='Raw ECG')
        plt.title('The result on the raw ECG')
        # plt.plot(QRS_ind,QRS_amp,'ro',label='QRS Locations')
        plt.plot(QRS_ind, QRS_amp, 'ro', label='QRS Locations')
        plt.show()
    return QRS_amp, QRS_ind

if __name__ == '__main__':
    data = sio.loadmat('M.mat')
    M = data['M']
    QRS_amp, QRS_ind = DS_detect(M[0],1)