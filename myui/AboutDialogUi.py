# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\zhangs\Documents\Qt_Projects\Python\MyProject\Spec2.0\myui\AboutDialogUi.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(AboutDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.webViewTB = QtWidgets.QTextBrowser(AboutDialog)
        self.webViewTB.setObjectName("webViewTB")
        self.gridLayout.addWidget(self.webViewTB, 0, 0, 1, 1)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "Dialog"))
