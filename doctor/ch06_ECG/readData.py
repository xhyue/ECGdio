import matplotlib.pyplot as plt
# import DS_detect
import scipy.io as sio
# ------ LOAD HEADER DATA --------------------------------------------------
# ------ 读入头文件数据 -----------------------------------------------------
#
# 示例：用记事本打开的117.hea 文件的数据
#
#      117 2 360 650000
#      117.dat 212 200 11 1024 839 31170 0 MLII
#      117.dat 212 200 11 1024 930 28083 0 V2
#      # 69 M 950 654 x2
#      # None
#
#-------------------------------------------------------------------------
def read_hea(PATH,HEADERFILE):
    print('WORKING ON ' + HEADERFILE)  # 在命令行窗口提示当前工作状态
    f = open(PATH + HEADERFILE, 'r')
    dataset = f.readlines()
    datalines = []
    for line in dataset:
        # 去除换行符
        temp1 = line.strip('\n')
        # 按照tab对字符串进行切片
        temp2 = temp1.split(' ')
        # 加入处理好的数据，还是str类型
        datalines.append(temp2)
    nosig = int(datalines[0][1])  # 信号通道数目
    sfreq = int(datalines[0][2])  # 数据采样频率
    dformat = []  # 信号格式; 这里只允许为 212 格式
    gain = []  # 每 mV 包含的整数个数
    bitres = []  # 采样精度（位分辨率）
    zerovalue = []  # ECG 信号零点相应的整数值
    firstvalue = []  # 信号的第一个整数值 (用于偏差测试)
    for i in range(nosig):  # 读取每个通道信号的数据信息
        dformat.append(int(datalines[i+1][1]))
        gain.append(int(datalines[i+1][2]))
        bitres.append(int(datalines[i+1][3]))
        zerovalue.append(int(datalines[i+1][4]))
        firstvalue.append(int(datalines[i+1][5]))
    return nosig,sfreq,dformat,gain,bitres,zerovalue,firstvalue

# ------ LOAD BINARY DATA --------------------------------------------------
# ------ 读取 ECG 信号二值数据 ----------------------------------------------
def read_dat(PATH,DATAFILE,dformat,SAMPLES2READ,nosig,zerovalue,firstvalue,gain,sfreq):
    if dformat != [212,212]:
        print("this script does not apply binary formats different to 212!")

    print('WORKING ON ' + DATAFILE)  # 在命令行窗口提示当前工作状态
    f = open(PATH + DATAFILE, 'rb')
    dataset = f.read()
    data = [[],[],[]]
    k = 0
    for i in range(SAMPLES2READ):
        for j in range(3):
            data[j].append(dataset[k])
            k = k+1
    # 通过一系列的移位（bitshift）、位与（bitand）运算，将信号由二值数据转换为十进制数
    # 字节向右移四位，即取字节的高四位
    M2H = []
    for i in range(SAMPLES2READ):
        M2H.append(data[1][i]>>4)
    # 取字节的低四位
    M1H = []
    for i in range(SAMPLES2READ):
        M1H.append(data[1][i] & 15)
    PRL = []
    PRR = []
    for i in range(SAMPLES2READ):
        # sign-bit   取出字节低四位中最高位，向右移九位
        PRL.append((data[1][i] & 8) << 9)
        # sign-bit   取出字节高四位中最高位，向右移五位
        PRR.append((data[1][i] & 128) << 5)
    M = [[],[]]
    for i in range(SAMPLES2READ):
        temp1 = (M1H[i] <<8 ) + data[0][i] - PRL[i]
        temp2 = (M1H[i] << 8) + data[2][i] - PRR[i]
        M[0].append(temp1)
        M[1].append(temp2)
    if M[0][0]!=firstvalue[0] and M[0][1]!=firstvalue[1]:
        print("inconsistency in the first bit values")
    Time = []
    if nosig == 2:
        for i in range(SAMPLES2READ):
            M[0][i] = (M[0][i]-zerovalue[0])/gain[0]
            M[1][i] = (M[1][i]-zerovalue[1])/gain[1]
            Time.append(i/sfreq)
    return Time,M

# ------ LOAD ATRFILE DATA --------------------------------------------------
# ------ 读入标记文件数据 -----------------------------------------------------
def read_atr(PATH,ATRFILE,sfreq,Time,SAMPLES2READ):
    print('WORKING ON ' + ATRFILE)  # 在命令行窗口提示当前工作状态
    f = open(PATH + ATRFILE, 'rb')
    dataset = f.read()
    data = [[],[]]
    for i in range(0,len(dataset),2):
        data[0].append(dataset[i])
        data[1].append(dataset[i+1])
    sa = len(data[0])
    ATRTIME = []
    ANNOT = []
    i = 0
    while i<sa :
        i = int(i)
        annoth = int(data[1][i])>>2
        if annoth == 59 :
            temp = data[0][i+2]+data[1][i+2]<<8+data[0][i+1]<<16+data[1][i+1]<<24
            ANNOT.append(data[1][i+3]>>2)
            ATRTIME.append(temp)
            i = i+3
        elif annoth ==63:
            hilfe = ((data[1][i] & 3) << 8) + data[0][i]
            hilfe = hilfe + hilfe % 2
            i = i + hilfe/2
        else:
            temp = ((data[1][i] & 3) << 8)+data[0][i]
            ATRTIME.append(temp)
            ANNOT.append(data[1][i]>>2)
        i = i+1
    ANNOT = ANNOT[0:len(ANNOT)-2]  # last line = EOF (=0)
    ATRTIME = ATRTIME[0:len(ATRTIME)-2]  # last line = EOF (=0)
    # 累计和
    for i in range(1,len(ATRTIME)):
        ATRTIME[i] = ATRTIME[i - 1] + ATRTIME[i]
    for i in range(len(ATRTIME)):
        ATRTIME[i] = ATRTIME[i] / sfreq
    index = [i for i in range(len(ATRTIME)) if ATRTIME[i] <= Time[SAMPLES2READ-1]]
    ATRTIMED = []
    ANNOTD = []
    for i in range(len(index)):
        ATRTIMED.append(ATRTIME[i])
        ANNOTD.append(int(ANNOT[i]))
    return ANNOTD,ATRTIMED

# ------ DISPLAY DATA ------------------------------------------------------
def display_data(Time,M, patname):
    plt.xlabel('Time / s')
    plt.ylabel('Voltage / mV')
    plt.title('ECG signal ')
    plt.plot(Time,M[1])
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("@@@@@@", BASE_DIR)
    plt.savefig(BASE_DIR+"/file/" + patname + ".png")
    # plt.show()
# ------ SPECIFY DATA ------------------------------------------------------
# ------ 指定数据文件 -------------------------------------------------------
# def exec_create_img(headerfile, atrfile, datafile):
#     PATH= ''   # 指定数据的储存路径
#     HEADERFILE= str(headerfile)      # .hea 格式，头文件，可用记事本打开
#     ATRFILE = str(atrfile)         # .atr 格式，属性文件，数据格式为二进制数
#     DATAFILE= str(datafile)         # .dat 格式，ECG 数据
#     SAMPLES2READ=1800          # 指定需要读入的样本数
#     # 若.dat文件中存储有两个通道的信号:则读入 2*SAMPLES2READ 个数据
#     nosig,sfreq, dformat, gain, bitres, zerovalue, firstvalue = read_hea(PATH, HEADERFILE)
#     Time, M = read_dat(PATH, DATAFILE,dformat,SAMPLES2READ,nosig,zerovalue,firstvalue,gain,sfreq)
#     ANNOTD, ATRTIMED = read_atr(PATH,ATRFILE,sfreq,Time,SAMPLES2READ)
#     sio.savemat('M',{'M':M[0]})
#     display_data(Time, M)

