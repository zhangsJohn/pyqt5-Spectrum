# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\zhangs\Documents\Qt_Projects\Python\MyProject\Spec2.0\myui\HelpDialogUi.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_HelpDialog(object):
    def setupUi(self, HelpDialog):
        HelpDialog.setObjectName("HelpDialog")
        HelpDialog.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(HelpDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.webViewTB = QtWidgets.QTextBrowser(HelpDialog)
        self.webViewTB.setObjectName("webViewTB")
        self.gridLayout.addWidget(self.webViewTB, 0, 0, 1, 1)

        self.retranslateUi(HelpDialog)
        QtCore.QMetaObject.connectSlotsByName(HelpDialog)

    def retranslateUi(self, HelpDialog):
        _translate = QtCore.QCoreApplication.translate
        HelpDialog.setWindowTitle(_translate("HelpDialog", "Dialog"))
