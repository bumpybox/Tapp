# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Chucky\Documents\GitHub\Tapp\Maya\rigging\spherePreview\resources/dialog.ui'
#
# Created: Mon Mar 03 21:37:05 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(222, 70)
        MainWindow.setWindowOpacity(1.0)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.line_23 = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_23.sizePolicy().hasHeightForWidth())
        self.line_23.setSizePolicy(sizePolicy)
        self.line_23.setFrameShape(QtGui.QFrame.HLine)
        self.line_23.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_23.setObjectName("line_23")
        self.horizontalLayout_2.addWidget(self.line_23)
        self.character_fkik_label = QtGui.QLabel(self.centralwidget)
        self.character_fkik_label.setObjectName("character_fkik_label")
        self.horizontalLayout_2.addWidget(self.character_fkik_label)
        self.line_2 = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_2.addWidget(self.line_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.create_pushButton = QtGui.QPushButton(self.centralwidget)
        self.create_pushButton.setObjectName("create_pushButton")
        self.horizontalLayout.addWidget(self.create_pushButton)
        self.delete_pushButton = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.delete_pushButton.sizePolicy().hasHeightForWidth())
        self.delete_pushButton.setSizePolicy(sizePolicy)
        self.delete_pushButton.setObjectName("delete_pushButton")
        self.horizontalLayout.addWidget(self.delete_pushButton)
        self.help_pushButton = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.help_pushButton.sizePolicy().hasHeightForWidth())
        self.help_pushButton.setSizePolicy(sizePolicy)
        self.help_pushButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.help_pushButton.setObjectName("help_pushButton")
        self.horizontalLayout.addWidget(self.help_pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Sphere Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.character_fkik_label.setText(QtGui.QApplication.translate("MainWindow", "Sphere Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.create_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Create", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Delete All", None, QtGui.QApplication.UnicodeUTF8))
        self.help_pushButton.setText(QtGui.QApplication.translate("MainWindow", "?", None, QtGui.QApplication.UnicodeUTF8))

