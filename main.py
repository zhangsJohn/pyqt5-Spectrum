import sys
import time
import serial
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMenu
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer, QThreadPool,QUrl
from helper.mydialogs import SerialDialog,HelpDialog,AboutDialog
from myui.MainUi import Ui_MainWindow
from helper.utils import *
from helper.fit_utils import *
#from fbs_runtime.application_context.PyQt5 import ApplicationContext


class MainWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()  # 加载主窗体元素,调整设置窗口位置大小
        self.loadStyle()
        self.initData()
        # self.loadCofig()    # 读取上次参数设置到加载内存，这里主要是串口的参数

    def initData(self):
        self.msg = ''  # state状态框提示信息
        self.basetime = 0  # 用于LCD计时显示的初始时间
        self.timer = QTimer()
        self.threadpool = QThreadPool()
        self.serial_info = {}  # serial info dict
        self.sr = 0  # the handle for serial port
        self.work_mod = 0  # work mod, 0:Peak Mod, 1:Direct Mod
        self.ploths = [0, 0, 0]   # plot handle of spec/snap/cali
        self.plotWg = [self.specPlot, self.snapPlot, self.caliPlot]
        self.pack_flag = 255  # data package head/tail flag
        self.measure_inf = {'time': 100, 'ch': 1024,
                            'max_energy': 10000, 'ref_num': 100}
        self.stop_flag = 0  # begin_flag to control the loop of read thread
        # the LinearRegionItem handle(get the fit region)
        self.roi_handle = [0, 0, 0]
        # the boundary for curve fit region
        self.fit_region = [[1, 10], [1, 10], [1, 10]]
        self.roi = [0,0,0]   # menu action ROI
        self.fit = [0,0,0]  # menu action Fit
        self.fiths = [0, 0, 0]  # # fit handle of spec/snap/cali
        self.legend = [0,0,0]
        self.curr_index = 0

    def initUi(self):
        pg.setConfigOption('background', 'w')
        QApplication.setStyle('fusion')
        self.setupUi(self)

        # init the default method list for curve fit
        self.dropMethod.insertItems(0, METHOD_LIST[0])

        # 获取显示器分辨率大小
        desktop = QApplication.desktop()
        screenRect = desktop.screenGeometry()
        self.h = screenRect.height()
        self.w = screenRect.width()
        self.setGeometry(int(self.w*0.1), int(self.h*0.1), int(self.w*0.8), int(self.h*0.8))

    def loadStyle(self):
        try:
            with open('./qss/Aqua.qss') as f: 
                style = f.read() # 读取样式表
                self.setStyleSheet(style)
        except Exception as e:
            self.tbStates.setText(str(e))

    @pyqtSlot(int)
    def on_dropFitType_currentIndexChanged(self, index):
        self.dropMethod.clear()
        self.dropMethod.insertItems(0, METHOD_LIST[index])

    @pyqtSlot(int)
    def on_plotTabWidget_currentChanged(self, index):
        self.curr_index = index

    @pyqtSlot()
    def on_roi_triggered(self):
        currpage = self.curr_index
        if self.roi_handle[currpage] == 0:  # 新建选区
            self.roi_handle[currpage] = pg.LinearRegionItem(
                values=self.fit_region[currpage], bounds=[0, self.measure_inf['ch']])
            self.roi_handle[currpage].sigRegionChangeFinished.connect(
                self.on_region_changed)
            self.plotWg[currpage].addItem(
                self.roi_handle[currpage], ignoreBounds=True)
        else:   # 选取存在，再次点击picker取消选取
            self.plotWg[currpage].removeItem(self.roi_handle[currpage])
            self.roi_handle[currpage] = 0

    @pyqtSlot()
    def on_fit_triggered(self):
        currpage = self.curr_index
        if self.fiths[currpage] == 0:  # 新建选区
            self.fit[currpage].setChecked(True)
            self.fiths[currpage] = self.plotWg[currpage].plotItem.plot()
            self.fiths[currpage].setPen((100, 200, 100))
        else:   # 选取存在，再次点击picker取消选取
            self.fit[currpage].setChecked(False)
            self.plotWg[currpage].removeItem(self.fiths[currpage])
            self.fiths[currpage] = 0

    def on_region_changed(self):
        currpage = self.curr_index
        self.fit_region[currpage] = self.roi_handle[currpage].getRegion()

    @pyqtSlot()
    def on_packFlagPB_clicked(self):
        flag = int(self.packFlagLE.text())
        if flag >=0 and flag <=255:
            self.pack_flag = flag
            self.msg += self.packFlagLE.text() + '\n'
        else:
            self.msg += '输入有误，请输入0-255数字'
        self.tbStates.setText(self.msg)

    @pyqtSlot()
    def on_fdMaxPB_clicked(self):
        if self.fdMaxPB.text()=='find max':
            self.fdMaxPB.setText('stop find')
            if self.basetime!=0:    # 如果正在测量先停止测量
                self.on_pbStop_clicked()
            if self.manage_serial(1):
                self.maxvalue = 0
                self.findnum = 0
                self.start_read_thread(1)
        else:
            self.fdMaxPB.setText('find max')
            self.stop_flag = 1
            self.manage_serial(0)
        self.tbStates.setText(self.msg)

    @pyqtSlot(int)
    def on_modCB_currentIndexChanged(self, index):
        self.work_mod = index
        self.msg += self.modCB.currentText() + '\n'
        self.tbStates.setText(self.msg)

    @pyqtSlot()
    def on_pbStart_clicked(self):
        """
        1.open serial port
        2.build plot and start readThread
        3.start timer to update states
        """
        if self.manage_serial(1):
            self.build_plots()
            self.buff = 0  
            self.start_read_thread()  # TODO:  'start_read' more ways
            self.start_timer()
        self.tbStates.setText(self.msg)

    @pyqtSlot()
    def on_pbSnap_clicked(self):
        if self.ploths != [0, 0, 0]:
            self.ploths[1].setData(self.ploths[0].yData)
            self.msg += 'get the copy of spec data!\n'
            self.plotTabWidget.setCurrentIndex(1)
        else:
            self.msg += 'there is nothing to copy!\n'
        self.tbStates.setText(self.msg)

    @pyqtSlot()
    def on_pbStop_clicked(self):
        """
        1.close serial port
        2.stop timer and clear readThread
        """
        self.stop_flag = 1  # 停止线程读取数据
        self.manage_serial(0)
        self.timer.stop()  # 结束计时器更新
        self.basetime = 0
        self.tbStates.setText(self.msg)

    @pyqtSlot()
    def on_pbFitCurve_clicked(self):
        currpage = self.curr_index
        if currpage==0 and self.basetime != 0:
            self.tbStates.setText('正在读取能谱，请停止读取或于snap区拟合\n')
            return 0
        if self.fiths[currpage] == 0:
            self.msg += 'fit is not enabled\n'
        else:
            L = int(self.fit_region[currpage][0])
            R = int(self.fit_region[currpage][1])
            # 获取拟合目标区域的数据
            xdata = self.ploths[currpage].xData
            ydata = self.ploths[currpage].yData
            sel_ydata = ydata[L:R]
            sel_xdata = xdata[L:R]
            # 选取拟合方式，配置拟合参数
            info = self.get_fit_info()
            fid = info['fid']
            fun = info['fun']
            guess = info['p0']
            if fid[0] == 0: # 对于常用的高斯拟合做一些参数预配置
                guess[0] = max(ydata)
                guess[1] = (L+R)/2
            # 获取当前拟合函数，得到拟合参数绘制拟合曲线
            try:
                if fid[0]==4:  # 插值绘图
                    f = interp1d(sel_xdata, sel_ydata, kind=fun)
                    new_x = np.linspace(min(sel_xdata),max(sel_xdata),len(sel_xdata)*5)
                    self.fiths[currpage].setData(y=f(new_x), x=new_x)
                else:   # 最小二乘法
                    popt = curve_fit(fun, sel_xdata, sel_ydata, p0=guess)[0]
                    self.fiths[currpage].setData(y=fun(xdata, *popt), x=xdata)
                    # 显示更多拟合信息
                    if fid[0]==0:
                        FWHM = popt[2]*2.355
                        res = FWHM/popt[1]*100
                        self.msg = '拟合参数：\n'+str(popt)+'\n'+\
                            '拟合区间：' + str([L, R])+'\n' +\
                            '分辨率：'+str(res)+'\n'
                        self.tbEquation.setText(fun.__doc__)
                    else:
                        self.msg = '拟合参数：\n'+str(popt)+'\n'
            except Exception as e:
                self.msg += str(e)+'\n'
            finally:
                self.tbStates.setText(self.msg)
        self.tbStates.setText(self.msg)

    def get_fit_info(self):
        # update the fitfun_info,display the fun string
        # self.fitfun_info = {'index':[0, 0], 'fun':gauss1, 'pnum':3}
        ftype = self.dropFitType.currentIndex()
        index = self.dropMethod.currentIndex()
        pnum = 3
        if ftype==4:
            fn_obj = METHOD_LIST[ftype][index]
        else:
            fn_obj = getattr(sys.modules[__name__], METHOD_LIST[ftype][index])
            # 获取拟合配置额外参数信息
            if ftype == 0:  # gauss
                pnum = 3*(index+1)
            elif ftype == 1:    # poly
                pnum = index+2
            elif ftype == 2:    # exp
                pnum = 2*(index+1)
            elif ftype == 3:    # power
                pnum = index+2
        p0 = [1 for i in range(pnum)]   # 默认参数配置，全1
        return {'fid':[ftype,index],'fun':fn_obj,'p0':p0}

    @pyqtSlot()
    def on_pbDel_clicked(self):
        num = self.tableCali.rowCount()
        if num <= 2:
            self.msg += 'two item at least !\n'
        else:
            self.msg += 'del row'+str(num)+'\n'
            self.tableCali.removeRow(num-1)
        self.tbStates.setText(self.msg)
    
    @pyqtSlot()
    def on_pbAdd_clicked(self):
        num = self.tableCali.rowCount()
        self.tableCali.insertRow(num)
        self.msg += 'add row'+str(num)+'\n'
        self.tbStates.setText(self.msg)

    @pyqtSlot()
    def on_setTimePB_clicked(self):
        self.measure_inf['time'] = int(self.measTimeLE.text())

    @pyqtSlot()
    def on_setChPB_clicked(self):
        self.measure_inf['ch'] = int(self.chNumLE.text())

    @pyqtSlot()
    def on_setMaxEPB_clicked(self):
        self.measure_inf['max_energy'] = int(self.maxELE.text())

    @pyqtSlot()
    def on_setRefNumPB_clicked(self):
        self.measure_inf['ref_num'] = int(self.refNumLE.text())     

    @pyqtSlot()
    def on_pbCaliSubmit_clicked(self):
        self.plotTabWidget.setCurrentIndex(2)
        if self.ploths == [0,0,0]:
            self.build_plots()
        if self.fiths[2] == 0:  # 新建选区
            self.on_fit_triggered()
        # 读取table数据
        num = self.tableCali.rowCount()
        try:
            xdata = [int(self.tableCali.item(i,0).text()) for i in range(num)]
            ydata = [int(self.tableCali.item(i,1).text()) for i in range(num)]
        except:
            self.tbStates.setText('请检查设置点是否完整')
            return 0
        # 默认的np.polyfit一阶拟合
        fun = np.polyfit(xdata,ydata, deg=1)
        fitY = np.polyval(fun, xdata)
        self.msg = '截距:%.2f\n斜率%.5f' % (fun[1], fun[0])
        self.fit_paras = {'slope':fun[0], 'intercept':fun[1]}
        # 绘制数据点和拟合直线
        self.ploths[2].setData(y=ydata,x=xdata)
        self.fiths[2].setData(x=xdata, y=fitY)
        self.tbStates.setText(self.msg)

    @pyqtSlot()
    def on_pbCaliApply_clicked(self):
        if self.pbCaliApply.text()=='Apply':
            self.pbCaliApply.setText('Cancle Apply')
        else:
            self.pbCaliApply.setText('Apply')


    @pyqtSlot()
    def on_actionSerial_triggered(self):
        sd = SerialDialog()
        if sd.exec_():  # 执行方法，成为模态对话框，用户点击OK后，返回1
            self.serial_info = sd.get_content()  # 获取串口配置信息，用于连接串口使用
            self.msg += str(self.serial_info) + '\n'
            self.tbStates.setText(self.msg)

    @pyqtSlot()
    def on_actionHelp_triggered(self):
        hd = HelpDialog()
        url = QUrl("HELP.html")
        hd.webViewTB.setSource(url)
        hd.setGeometry(int(self.w*0.3), int(self.h*0.1), int(self.w*0.4), int(self.h*0.8))
        hd.exec_()

    @pyqtSlot()
    def on_actionProject_triggered(self):
        ad = AboutDialog()
        url = QUrl("Project.html")
        ad.webViewTB.setSource(url)
        ad.setGeometry(int(self.w*0.3), int(self.h*0.1), int(self.w*0.4), int(self.h*0.8))
        ad.exec_()

    @pyqtSlot()
    def on_actionInput_triggered(self):
        filename, filetype = QFileDialog.getOpenFileName(
            self, 'Open File', '.')
        if filename:
            try:
                data = np.loadtxt(filename, dtype=int)  # load 时也要指定为逗号分隔
                if self.ploths == [0, 0, 0]:
                    self.build_plots()
                if self.basetime == 0:
                    self.update_plot(data[:, 1],data[:,0],0)
                else:
                    self.update_plot(data[:, 1],data[:,0],1)
                    self.plotTabWidget.setCurrentIndex(1)
            except Exception as e:
                self.msg += str(e) + '\n'
            finally:
                self.tbStates.setText(self.msg)

    @pyqtSlot(int)
    def on_textCKB_stateChanged(self,state):
        index = self.curr_index
        if state:
            self.plotWg[index].plotItem.setLabels(title=self.titleLE.text(),\
                left=self.axisyLE.text(), bottom=self.axisxLE.text())
        else:
            self.plotWg[index].plotItem.setTitle(title=None)
            self.plotWg[index].plotItem.showLabel('left',False)
            self.plotWg[index].plotItem.showLabel('bottom',False)

    @pyqtSlot(int)
    def on_legendCKB_stateChanged(self,state):
        index = self.curr_index
        if self.legend[index]!=0:
            self.plotWg[index].plotItem.getViewBox().removeItem(self.legend[index])
            self.legend[index]=0
        if state:          
            self.legend[index] = self.plotWg[index].plotItem.addLegend()
            if self.ploths[index]!=0:
                self.legend[index].addItem(self.ploths[index],self.legendLE2.text())
            else:
                self.tbStates.setText('no data')
                
            if self.fiths[index]!=0:
                self.legend[index].addItem(self.fiths[index],self.legendLE1.text())
            else:
                self.tbStates.setText('no fit')

    def manage_serial(self, op):
        """
        bref: help manage the serial(construct/open, close)

        paras: 
            op: 0：close, 1:open

        return: 0:fail, 1:success
        """
        try:
            if op:  # 如果是开启指令，则执行串口连接
                inf = self.serial_info
                self.sr = serial.Serial(port=inf['port'],   # 创建同时就会开启串口
                                        baudrate=inf['baudRate'],
                                        bytesize=inf['dataBit'],
                                        parity=inf['testType'],
                                        stopbits=inf['stopBit'],
                                        timeout=inf['timeOut'])
                self.serialLed.set_state(1)
                self.msg += 'open ' + inf['port'] + '\n'
            else:
                self.sr.close()
                self.sr = 0
                self.serialLed.set_state(0)
                self.msg += 'close serial port' + '\n'
        except Exception as e:
            self.sr = 0
            self.serialLed.set_state(0)
            self.msg += str(e) + '\n'
            return 0
        return 1

    def start_timer(self):
        self.basetime = time.time()
        self.timeLCD.setDigitCount = 4
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start(1000)

    def recurring_timer(self):
        t = int(time.time()-self.basetime)
        self.timeLCD.display(t)
        if t == self.measure_inf['time']:
            self.on_pbStop_clicked()


    def build_plots(self):
        '''init the three plot canvas, save the handles to update plot later'''
        ch = self.measure_inf['ch']
        xdata = np.linspace(1, ch, ch)
        for i in range(3):
            if self.ploths[i] == 0:
                self.ploths[i] = self.plotWg[i].plotItem.plot(symbol='+',size=2)
                self.roi[i] = self.plotWg[i].plotItem.getViewBox(
                ).menu.addAction('ROI')
                self.roi[i].setCheckable(True)
                self.roi[i].triggered.connect(self.on_roi_triggered)
                self.fit[i] = self.plotWg[i].plotItem.getViewBox(
                ).menu.addAction('Fit')
                self.fit[i].setCheckable(True)
                self.fit[i].triggered.connect(self.on_fit_triggered)
            self.ploths[i].setPen((228, 128, 130))
            self.ploths[i].setData(y=xdata, x=xdata)

    def start_read_thread(self,mod=0):
        if mod==0:
            worker = Worker(self.execute_read_fun)
            # worker.signals.finished.connect(self.thread_complete)
            # worker.signals.error.connect(self.thread_error)
            worker.signals.result.connect(self.update_plot)
        else:
            worker = Worker(self.execute_find_fun)
            # worker.signals.finished.connect(self.thread_complete)
            # worker.signals.error.connect(self.thread_error)
            worker.signals.state.connect(self.update_max)
        # Execute
        self.stop_flag = 0
        self.threadpool.start(worker)

    @pyqtSlot(object,object,int)
    def update_plot(self, ydata,xdata,index):
        if self.pbCaliApply.text()!='Apply':
            a = self.fit_paras['slope']
            b = self.fit_paras['intercept']
            xdata= a*xdata+b
        if self.basetime!=0 and self.work_mod == 0:
            ydata += self.buff
            self.buff = ydata
        self.ploths[index].setData(y=ydata,x=xdata)
    
    @pyqtSlot(dict)
    def update_max(self,dict):
        if self.maxvalue < dict['maxvalue']:
            self.maxvalue = dict['maxvalue']
            print(self.maxvalue)
            self.fdMaxLE.setText(str(self.maxvalue))
        self.findnum += dict['num']
        self.tbStates.setText('当前读取数目：'+str(self.findnum))

    def execute_find_fun(self, result_callback,state_callback):
        while True:
            print('run')
            if self.stop_flag:
                self.msg += 'find max thread stopped\n'
                break
            try:
                cache = self.sr.read(self.measure_inf['ref_num'] * 6)
            except serial.SerialException as e:
                continue
            buff = byte_shift(unpack(cache, self.pack_flag, 5))
            num = len(buff)
            maxvalue = max(buff)[0]
            state_callback.emit({'num':num,'maxvalue':maxvalue})

    def execute_read_fun(self, result_callback, state_callback):
        # 这里我们可以利用self,读取主线程的msg/stop_flag等变量,但是不能调用主线程的widget更新GUI的方法
        while True:
            print('run')
            if self.stop_flag:
                self.msg += 'read thread stopped\n'
                break
            ch = self.measure_inf['ch']  # 能谱道数（x轴长度）
            # 对arm传输的数据格式进行解析，缓存到ydata用于绘图更新
            ydata = np.linspace(1, ch, ch)
            xdata = np.linspace(1, ch, ch)
            if self.work_mod:   # 模式1:直接接收能谱
                try:
                    # 读取能谱数据包（data + package tail）
                    all_read = self.sr.read(ch*4 + 1)
                except serial.SerialException as e:
                    continue
                if all_read[-1] == self.pack_flag:
                    all_read = all_read[0:-1]
                    ydata = byte_shift(np.asarray(bytearray(all_read))
                                       .reshape([int(len(all_read)/4), 4]))[:,0]
                else:
                    self.sr.reset_input_buffer()
            else:   # 模式0：读取波形峰面积数据手动生成能谱,每个数据包为5个字节
                try:
                    cache = self.sr.read(self.measure_inf['ref_num'] * 6)
                except serial.SerialException as e:
                    continue
                buff = byte_shift(unpack(cache, self.pack_flag, 5)) / \
                    self.measure_inf['max_energy'] * ch  # 缩放数据到道址范围内
                range_data = np.linspace(0, ch , ch + 1)
                ydata, bins = np.histogram(buff, range_data)
                xdata = bins[0:-1]
            result_callback.emit(ydata,xdata,0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MainWin()
    myWin.show()
    sys.exit(app.exec_())
