# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '\\bumpyboxnas\bumpybox\tools\Tapp\Maya\rigging\resources/dialog.ui'
#
# Created: Thu Apr 03 10:10:43 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(178, 273)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
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
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.central_verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.latticeAdd_pushButton = QtGui.QPushButton(self.centralwidget)
        self.latticeAdd_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.latticeAdd_pushButton.setObjectName("latticeAdd_pushButton")
        self.horizontalLayout_2.addWidget(self.latticeAdd_pushButton)
        self.latticeRemove_pushButton = QtGui.QPushButton(self.centralwidget)
        self.latticeRemove_pushButton.setMinimumSize(QtCore.QSize(0, 40))
        self.latticeRemove_pushButton.setObjectName("latticeRemove_pushButton")
        self.horizontalLayout_2.addWidget(self.latticeRemove_pushButton)
        self.central_verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.central_verticalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.doraSkin_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Dora Skin", None, QtGui.QApplication.UnicodeUTF8))
        self.sculptInbetweenEditor_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Sculpt Inbetween Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.zvRadialBlendshape_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Zv Radial Blendshape", None, QtGui.QApplication.UnicodeUTF8))
        self.ngSkinTools_pushButton.setText(QtGui.QApplication.translate("MainWindow", "ngSkinTools", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Lattice", None, QtGui.QApplication.UnicodeUTF8))
        self.latticeAdd_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.latticeRemove_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))

