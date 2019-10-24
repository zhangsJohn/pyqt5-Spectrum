import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QDialog, QInputDialog
from PyQt5.QtCore import pyqtSlot
from myui.SerialDialogUi import Ui_SrDialog
from myui.AppearanceDialogUi import Ui_AppearanceDialog

class SerialDialog(QDialog, Ui_SrDialog):
    '''manage the serial setting dialog '''
    def __init__(self, parent=None):
        super(SerialDialog, self).__init__(parent)
        self.setupUi(self)
        self._baudrates = ['460800', '1200', '1800', '2400', '4800', '9600', '19200', '38400', \
            '57600', '115200', '自定义']
        self._parity = {'None':serial.PARITY_NONE, 'Even':serial.PARITY_EVEN, 'Odd':serial.PARITY_ODD}
        self._stopbits = {'1':serial.STOPBITS_ONE, '1.5':serial.STOPBITS_ONE_POINT_FIVE, '2':serial.STOPBITS_TWO}
        self.update_port_list()
        self.update_baudrates()

    def update_port_list(self):
        '''refresh and display the current available serial ports in PC '''
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) <= 0:
            port_list = ['No device']
        else:
            j = 0
            for i in list(port_list):
                port_list[j] = i[0]  # just get the port name like COM1
                j = j+1
            self.portCB.insertItems(0, port_list)

    def update_baudrates(self):
        self.baudRateCB.insertItems(0, self._baudrates)
        self.baudRateCB.currentIndexChanged.connect(self.edit_baudrate)

    @pyqtSlot(int)
    def edit_baudrate(self, index):
        if index == (len(self._baudrates)-1):
            text, okpressed = QInputDialog.getText(self, "自定义波特率", "Your baudRate:")
            if okpressed and text != '':
                self.baudRateCB.setItemText(0, text)
            self.baudRateCB.setCurrentIndex(0)

    def get_content(self):
        '''get the paras for the init of serial port'''
        data = {}
        data['port'] = self.portCB.currentText()
        data['baudRate'] = self.baudRateCB.currentText()
        data['stopBit'] = self._stopbits[self.stopBitCB.currentText()]
        data['dataBit'] = int(self.dataBitCB.currentText())
        data['testType'] = self._parity[self.testCB.currentText()]   
        data['timeOut'] = float(self.timeOutEt.text())
        return data
        
