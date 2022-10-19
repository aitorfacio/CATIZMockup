# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'catiz.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1305, 845)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tacsit = QtWidgets.QLabel(self.centralwidget)
        self.tacsit.setGeometry(QtCore.QRect(0, 40, 1021, 741))
        self.tacsit.setObjectName("tacsit")
        self.zoom_in = QtWidgets.QPushButton(self.centralwidget)
        self.zoom_in.setGeometry(QtCore.QRect(1100, 160, 75, 23))
        self.zoom_in.setObjectName("zoom_in")
        self.zoom_out = QtWidgets.QPushButton(self.centralwidget)
        self.zoom_out.setGeometry(QtCore.QRect(1180, 160, 75, 23))
        self.zoom_out.setObjectName("zoom_out")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1305, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tacsit.setText(_translate("MainWindow", "TextLabel"))
        self.zoom_in.setText(_translate("MainWindow", "+"))
        self.zoom_out.setText(_translate("MainWindow", "-"))

