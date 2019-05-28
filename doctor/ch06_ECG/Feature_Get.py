import scipy.io as sio
import pywt
import numpy as np

Data = sio.loadmat('Feature.mat')
data = Data['feature'][0]
# 使信号的均值为0，去掉基线的影响
a=np.mean(data)
data = data- np.mean(data)
print(data.shape)
# db6小波5级分解
features = pywt.wavedec(data,'db6',level=5)
feature = []
for i in range(len(features)):
    feature = np.hstack((feature,features[i]))

print(feature.shape[0])