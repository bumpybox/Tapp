# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\toke.jepsen\Documents\GitHub\Tapp\Tapp\Maya\lighting\region\resources\region.ui'
#
# Created: Thu Oct 24 15:39:08 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(392, 259)
        MainWindow.setAcceptDrops(False)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.renderlayer_listWidget = QtGui.QListWidget(self.centralwidget)
        self.renderlayer_listWidget.setObjectName("renderlayer_listWidget")
        self.horizontalLayout.addWidget(self.renderlayer_listWidget)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.refresh_pushButton = QtGui.QPushButton(self.centralwidget)
        self.refresh_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.refresh_pushButton.setObjectName("refresh_pushButton")
        self.verticalLayout.addWidget(self.refresh_pushButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.getPreviewRegion_pushButton = QtGui.QPushButton(self.centralwidget)
        self.getPreviewRegion_pushButton.setObjectName("getPreviewRegion_pushButton")
        self.verticalLayout.addWidget(self.getPreviewRegion_pushButton)
        self.getObjectRegion_pushButton = QtGui.QPushButton(self.centralwidget)
        self.getObjectRegion_pushButton.setObjectName("getObjectRegion_pushButton")
        self.verticalLayout.addWidget(self.getObjectRegion_pushButton)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.connectPreview_pushButton = QtGui.QPushButton(self.centralwidget)
        self.connectPreview_pushButton.setObjectName("connectPreview_pushButton")
        self.verticalLayout.addWidget(self.connectPreview_pushButton)
        self.disconnectPreview_pushButton = QtGui.QPushButton(self.centralwidget)
        self.disconnectPreview_pushButton.setObjectName("disconnectPreview_pushButton")
        self.verticalLayout.addWidget(self.disconnectPreview_pushButton)
        self.connectArnold_pushButton = QtGui.QPushButton(self.centralwidget)
        self.connectArnold_pushButton.setObjectName("connectArnold_pushButton")
        self.verticalLayout.addWidget(self.connectArnold_pushButton)
        self.disconnectArnold_pushButton = QtGui.QPushButton(self.centralwidget)
        self.disconnectArnold_pushButton.setObjectName("disconnectArnold_pushButton")
        self.verticalLayout.addWidget(self.disconnectArnold_pushButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Region Render", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.getPreviewRegion_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Get Preview Region", None, QtGui.QApplication.UnicodeUTF8))
        self.getObjectRegion_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Get Object Region", None, QtGui.QApplication.UnicodeUTF8))
        self.connectPreview_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Connect Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.disconnectPreview_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Disconnect Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.connectArnold_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Connect Arnold", None, QtGui.QApplication.UnicodeUTF8))
        self.disconnectArnold_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Disconnect Arnold", None, QtGui.QApplication.UnicodeUTF8))

