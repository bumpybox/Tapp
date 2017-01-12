# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Chucky\Documents\GitHub\Tapp\Maya\animation\tools\resetAttributes\resources/dialog.ui'
#
# Created: Mon Mar 03 21:28:19 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(201, 116)
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
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.translation_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.translation_checkBox.setChecked(True)
        self.translation_checkBox.setObjectName("translation_checkBox")
        self.gridLayout.addWidget(self.translation_checkBox, 0, 0, 1, 1)
        self.rotation_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.rotation_checkBox.setChecked(True)
        self.rotation_checkBox.setObjectName("rotation_checkBox")
        self.gridLayout.addWidget(self.rotation_checkBox, 0, 1, 1, 1)
        self.scale_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.scale_checkBox.setChecked(True)
        self.scale_checkBox.setObjectName("scale_checkBox")
        self.gridLayout.addWidget(self.scale_checkBox, 1, 0, 1, 1)
        self.extraAttributes_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.extraAttributes_checkBox.setChecked(True)
        self.extraAttributes_checkBox.setObjectName("extraAttributes_checkBox")
        self.gridLayout.addWidget(self.extraAttributes_checkBox, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Reset Attributes", None, QtGui.QApplication.UnicodeUTF8))
        self.character_fkik_label.setText(QtGui.QApplication.translate("MainWindow", "Reset Attributes", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Reset Selection", None, QtGui.QApplication.UnicodeUTF8))
        self.translation_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Translation", None, QtGui.QApplication.UnicodeUTF8))
        self.rotation_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Rotation", None, QtGui.QApplication.UnicodeUTF8))
        self.scale_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Scale", None, QtGui.QApplication.UnicodeUTF8))
        self.extraAttributes_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Extra Attributes", None, QtGui.QApplication.UnicodeUTF8))

