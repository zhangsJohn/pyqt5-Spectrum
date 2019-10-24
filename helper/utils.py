import time
import traceback
import sys
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QObject


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress 

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    state = pyqtSignal(dict)
    result = pyqtSignal(object,object,int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    @param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    @type callback: function
    @param args: Arguments to pass to the callback function
    @param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['result_callback'] = self.signals.result
        self.kwargs['state_callback'] = self.signals.state

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.finished.emit()  # Done


def byte_shift(data):
    '''data为N*M的数组dec list，每个元素代表一个字节，
    将每M个字节拼接形成一个新数据，返回N*1数组，'''
    out = np.zeros([len(data), 1])
    for i in range(len(data)):    # convert the hex data from serial into dec list
        for j in range(len(data[i])):
            out[i] = out[i] + (data[i, len(data[i])-j-1] << j*8)
    return out

def unpack(bytesdata, tail, size):
    '''
    @bref: 解包，将读取的字节串进行错误数据剔除以及数据格式的转换，返回代表能量信息的数组

    @param bytesdata: bytes数组, 由多个连续数据包组成，数据包具有相同的包尾

    @param tail: 数据包包尾

    @param size: 单个数据包的大小（单位为字节）
    '''
    arr = np.asarray(bytearray(bytesdata))
    buff = []   # 存用于hist的原始数据
    while True:
        index = np.where(arr == tail)[0]
        if len(arr) > size:
            if (arr[0] == tail) and (arr[size] == tail):
                ind = index[np.where(index % size != 0)]     # 找到传输出错的间断点
                if ind.size:
                    buff.extend(arr[0:index[np.where(index==ind[0])[0][0]-1]])     # 将前面符合要求的子串取下拼接
                    arr = arr[(ind[0]):len(arr)]     # 删除拼接的字串，对后面的子串重复运算
                else:
                    buff.extend(arr)
                    break
            else:
                arr = arr[(index[1]):len(arr)]    # 删除前端起始位以前的不完整数据
        else:
            break
    return np.asarray(buff[0:-1]).reshape([int((len(buff)-1)/size), size])[:, 1:]


if __name__ == '__main__':
    orig = [1,2,3,255,
            2,2,3,255,
            3,2,3,255,
            4,2,3,255,9,
            5,2,3,255,
            6,2,
            7,2,3,255,
            8,2,3,255,
            9,2,3,255,
            10,3,255,
            11,2,3,255,
            12,2,3,255,
            13,2,3,255,
            14,2,3,255]
    data = bytes(orig)
    #print(orig[-5:len(orig)])
    print(unpack(data,255,4))
    #print(np.argwhere(np.asarray(orig)==9)[0][0])
