# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Chucky\Documents\GitHub\Tapp\Tapp\Maya\rigging\resources/rigging.ui'
#
# Created: Tue Nov 05 00:03:52 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(352, 655)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.doraSkin_pushButton = QtGui.QPushButton(self.centralwidget)
        self.doraSkin_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.doraSkin_pushButton.setObjectName("doraSkin_pushButton")
        self.verticalLayout.addWidget(self.doraSkin_pushButton)
        self.sculptInbetweenEditor_pushButton = QtGui.QPushButton(self.centralwidget)
        self.sculptInbetweenEditor_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.sculptInbetweenEditor_pushButton.setObjectName("sculptInbetweenEditor_pushButton")
        self.verticalLayout.addWidget(self.sculptInbetweenEditor_pushButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.doraSkin_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Dora Skin", None, QtGui.QApplication.UnicodeUTF8))
        self.sculptInbetweenEditor_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Sculpt Inbetween Editor", None, QtGui.QApplication.UnicodeUTF8))

