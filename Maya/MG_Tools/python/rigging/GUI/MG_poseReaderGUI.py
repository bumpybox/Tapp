from PyQt4 import QtCore, QtGui

import sip 
import maya.OpenMayaUI as apiUI
from maya import cmds , OpenMaya

import MG_Tools.python.rigging.script.MG_poseReader as MG_poseReader
reload(MG_poseReader)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(305, 199)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.nameL = QtGui.QLabel(self.groupBox)
        self.nameL.setObjectName(_fromUtf8("nameL"))
        self.gridLayout.addWidget(self.nameL, 0, 0, 1, 1)
        self.nameLE = QtGui.QLineEdit(self.groupBox)
        self.nameLE.setObjectName(_fromUtf8("nameLE"))
        self.gridLayout.addWidget(self.nameLE, 0, 1, 1, 1)
        self.sideL = QtGui.QLabel(self.groupBox)
        self.sideL.setObjectName(_fromUtf8("sideL"))
        self.gridLayout.addWidget(self.sideL, 1, 0, 1, 1)
        self.sideLE = QtGui.QLineEdit(self.groupBox)
        self.sideLE.setObjectName(_fromUtf8("sideLE"))
        self.gridLayout.addWidget(self.sideLE, 1, 1, 1, 1)
        self.poseObjectL = QtGui.QLabel(self.groupBox)
        self.poseObjectL.setObjectName(_fromUtf8("poseObjectL"))
        self.gridLayout.addWidget(self.poseObjectL, 2, 0, 1, 1)
        self.poseObjectLE = QtGui.QLineEdit(self.groupBox)
        self.poseObjectLE.setObjectName(_fromUtf8("poseObjectLE"))
        self.gridLayout.addWidget(self.poseObjectLE, 2, 1, 1, 1)
        self.pushButton = QtGui.QPushButton(self.groupBox)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 2, 2, 1, 1)
        self.aimAxisL = QtGui.QLabel(self.groupBox)
        self.aimAxisL.setObjectName(_fromUtf8("aimAxisL"))
        self.gridLayout.addWidget(self.aimAxisL, 3, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox, 3, 1, 1, 1)
        self.sizeL = QtGui.QLabel(self.groupBox)
        self.sizeL.setObjectName(_fromUtf8("sizeL"))
        self.gridLayout.addWidget(self.sizeL, 4, 0, 1, 1)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox.setProperty(_fromUtf8("value"), 1.0)
        self.doubleSpinBox.setObjectName(_fromUtf8("doubleSpinBox"))
        self.gridLayout.addWidget(self.doubleSpinBox, 4, 1, 1, 1)
        self.createPB = QtGui.QPushButton(self.groupBox)
        self.createPB.setObjectName(_fromUtf8("createPB"))
        self.gridLayout.addWidget(self.createPB, 5, 0, 1, 3)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.nameL.setText(QtGui.QApplication.translate("Form", "base name :", None, QtGui.QApplication.UnicodeUTF8))
        self.sideL.setText(QtGui.QApplication.translate("Form", "side : ", None, QtGui.QApplication.UnicodeUTF8))
        self.poseObjectL.setText(QtGui.QApplication.translate("Form", "pose object : ", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Form", "LOAD", None, QtGui.QApplication.UnicodeUTF8))
        self.aimAxisL.setText(QtGui.QApplication.translate("Form", "Aim Axis :", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(0, QtGui.QApplication.translate("Form", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(1, QtGui.QApplication.translate("Form", "Y", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(2, QtGui.QApplication.translate("Form", "Z", None, QtGui.QApplication.UnicodeUTF8))
        self.sizeL.setText(QtGui.QApplication.translate("Form", "size :", None, QtGui.QApplication.UnicodeUTF8))
        self.createPB.setText(QtGui.QApplication.translate("Form", "CREATE", None, QtGui.QApplication.UnicodeUTF8))

        self.customUi()
    
    def customUi(self):
        '''
        This procedure runs all the customizzation and overridings on the main ui
        '''
        self.connect( self.pushButton , QtCore.SIGNAL('clicked()') , self.loadPose )
        self.connect( self.createPB , QtCore.SIGNAL('clicked()') , self.createIt )
        
    def createIt(self):
        baseName = str(self.nameLE.text())
        side = str(self.sideLE.text())
        size = self.doubleSpinBox.value()
        axis = self.comboBox.currentIndex()
        pose = str(self.poseObjectLE.text())
        
        pr = MG_poseReader.MG_poseReader(baseName = baseName,
                                     side = side,
                                     poseInput = pose ,
                                     aimAxis = axis ,
                                     size  = size 
                                    
                                     )
        
        pr.create()
        
    def loadPose(self):
        sel = cmds.ls(sl = 1)[0]
        self.poseObjectLE.setText(sel)


    
def getMayaWindow():
    '''
    @brief         standard procedure used to get current Maya window (not for the users)
    '''
    ptr = apiUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class MG_poseReaderGUI(QtGui.QWidget, Ui_Form):
    '''
    @brief         this is the wrap class around our main widget , this is the class that gets instantiated and loaded
    '''
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent=getMayaWindow())
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.setupUi(self)

def show():
    ui=MG_poseReaderGUI()
    ui.show()