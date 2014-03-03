# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Chucky\Documents\GitHub\Tapp\Maya\rigging\resources/dialog.ui'
#
# Created: Mon Mar 03 22:10:22 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(143, 204)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.central_verticalLayout = QtGui.QVBoxLayout()
        self.central_verticalLayout.setObjectName("central_verticalLayout")
        self.doraSkin_pushButton = QtGui.QPushButton(self.centralwidget)
        self.doraSkin_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.doraSkin_pushButton.setObjectName("doraSkin_pushButton")
        self.central_verticalLayout.addWidget(self.doraSkin_pushButton)
        self.sculptInbetweenEditor_pushButton = QtGui.QPushButton(self.centralwidget)
        self.sculptInbetweenEditor_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.sculptInbetweenEditor_pushButton.setObjectName("sculptInbetweenEditor_pushButton")
        self.central_verticalLayout.addWidget(self.sculptInbetweenEditor_pushButton)
        self.zvRadialBlendshape_pushButton = QtGui.QPushButton(self.centralwidget)
        self.zvRadialBlendshape_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.zvRadialBlendshape_pushButton.setObjectName("zvRadialBlendshape_pushButton")
        self.central_verticalLayout.addWidget(self.zvRadialBlendshape_pushButton)
        self.ngSkinTools_pushButton = QtGui.QPushButton(self.centralwidget)
        self.ngSkinTools_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.ngSkinTools_pushButton.setObjectName("ngSkinTools_pushButton")
        self.central_verticalLayout.addWidget(self.ngSkinTools_pushButton)
        self.verticalLayout.addLayout(self.central_verticalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.doraSkin_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Dora Skin", None, QtGui.QApplication.UnicodeUTF8))
        self.sculptInbetweenEditor_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Sculpt Inbetween Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.zvRadialBlendshape_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Zv Radial Blendshape", None, QtGui.QApplication.UnicodeUTF8))
        self.ngSkinTools_pushButton.setText(QtGui.QApplication.translate("MainWindow", "ngSkinTools", None, QtGui.QApplication.UnicodeUTF8))

