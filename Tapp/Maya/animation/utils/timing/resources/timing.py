# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\tokejepsen\Documents\GitHub\Tapp\Tapp\Maya\animation\utils\timing\resources\timing.ui'
#
# Created: Sat Oct 05 18:06:33 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(513, 115)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 115))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.bake_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.bake_checkBox.setObjectName("bake_checkBox")
        self.horizontalLayout_3.addWidget(self.bake_checkBox)
        self.forwardOnly_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.forwardOnly_checkBox.setObjectName("forwardOnly_checkBox")
        self.horizontalLayout_3.addWidget(self.forwardOnly_checkBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.accurracy_doubleSpinBox = QtGui.QDoubleSpinBox(self.centralwidget)
        self.accurracy_doubleSpinBox.setObjectName("accurracy_doubleSpinBox")
        self.horizontalLayout.addWidget(self.accurracy_doubleSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.storeAnimation_pushButton = QtGui.QPushButton(self.centralwidget)
        self.storeAnimation_pushButton.setMinimumSize(QtCore.QSize(100, 40))
        self.storeAnimation_pushButton.setObjectName("storeAnimation_pushButton")
        self.horizontalLayout_2.addWidget(self.storeAnimation_pushButton)
        self.restoreAnimation_pushButton = QtGui.QPushButton(self.centralwidget)
        self.restoreAnimation_pushButton.setMinimumSize(QtCore.QSize(100, 40))
        self.restoreAnimation_pushButton.setObjectName("restoreAnimation_pushButton")
        self.horizontalLayout_2.addWidget(self.restoreAnimation_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_5.addLayout(self.verticalLayout)
        self.horizontalSlider = QtGui.QSlider(self.centralwidget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalLayout_5.addWidget(self.horizontalSlider)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Timing Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.bake_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Bake", None, QtGui.QApplication.UnicodeUTF8))
        self.forwardOnly_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Forward-only", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Accuracy:", None, QtGui.QApplication.UnicodeUTF8))
        self.storeAnimation_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Store Animation", None, QtGui.QApplication.UnicodeUTF8))
        self.restoreAnimation_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Restore Animation", None, QtGui.QApplication.UnicodeUTF8))

