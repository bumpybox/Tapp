from PyQt4 import QtCore, QtGui

import sip 
import maya.OpenMayaUI as apiUI
from maya import cmds , OpenMaya
from functools import partial
import MG_Tools.python.rigging.script.MG_splinePath as MG_splinePath
reload(MG_splinePath)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(342, 538)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.mainGB = QtGui.QGroupBox(Form)
        self.mainGB.setObjectName(_fromUtf8("mainGB"))
        self.gridLayout_2 = QtGui.QGridLayout(self.mainGB)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.baseNameL = QtGui.QLabel(self.mainGB)
        self.baseNameL.setObjectName(_fromUtf8("baseNameL"))
        self.gridLayout_2.addWidget(self.baseNameL, 0, 0, 1, 1)
        self.baseNameLE = QtGui.QLineEdit(self.mainGB)
        self.baseNameLE.setObjectName(_fromUtf8("baseNameLE"))
        self.gridLayout_2.addWidget(self.baseNameLE, 0, 2, 1, 5)
        self.sideL = QtGui.QLabel(self.mainGB)
        self.sideL.setObjectName(_fromUtf8("sideL"))
        self.gridLayout_2.addWidget(self.sideL, 1, 0, 1, 1)
        self.sideLE = QtGui.QLineEdit(self.mainGB)
        self.sideLE.setObjectName(_fromUtf8("sideLE"))
        self.gridLayout_2.addWidget(self.sideLE, 1, 2, 1, 5)
        self.samplesL = QtGui.QLabel(self.mainGB)
        self.samplesL.setObjectName(_fromUtf8("samplesL"))
        self.gridLayout_2.addWidget(self.samplesL, 2, 0, 1, 2)
        self.samplesSB = QtGui.QSpinBox(self.mainGB)
        self.samplesSB.setProperty(_fromUtf8("value"), 40)
        self.samplesSB.setObjectName(_fromUtf8("samplesSB"))
        self.gridLayout_2.addWidget(self.samplesSB, 2, 2, 1, 2)
        self.outputsL = QtGui.QLabel(self.mainGB)
        self.outputsL.setObjectName(_fromUtf8("outputsL"))
        self.gridLayout_2.addWidget(self.outputsL, 3, 0, 1, 2)
        self.outputsSB = QtGui.QSpinBox(self.mainGB)
        self.outputsSB.setProperty(_fromUtf8("value"), 30)
        self.outputsSB.setObjectName(_fromUtf8("outputsSB"))
        self.gridLayout_2.addWidget(self.outputsSB, 3, 2, 1, 2)
        self.offsetL = QtGui.QLabel(self.mainGB)
        self.offsetL.setObjectName(_fromUtf8("offsetL"))
        self.gridLayout_2.addWidget(self.offsetL, 4, 0, 1, 1)
        self.offsetSB = QtGui.QSpinBox(self.mainGB)
        self.offsetSB.setObjectName(_fromUtf8("offsetSB"))
        self.gridLayout_2.addWidget(self.offsetSB, 4, 2, 1, 2)
        self.inputCurveL = QtGui.QLabel(self.mainGB)
        self.inputCurveL.setObjectName(_fromUtf8("inputCurveL"))
        self.gridLayout_2.addWidget(self.inputCurveL, 5, 0, 1, 1)
        self.inputCurveLE = QtGui.QLineEdit(self.mainGB)
        self.inputCurveLE.setObjectName(_fromUtf8("inputCurveLE"))
        self.gridLayout_2.addWidget(self.inputCurveLE, 5, 1, 1, 5)
        self.inputCurvePB = QtGui.QPushButton(self.mainGB)
        self.inputCurvePB.setObjectName(_fromUtf8("inputCurvePB"))
        self.gridLayout_2.addWidget(self.inputCurvePB, 5, 6, 1, 1)
        self.firstupVecZL = QtGui.QLabel(self.mainGB)
        self.firstupVecZL.setObjectName(_fromUtf8("firstupVecZL"))
        self.gridLayout_2.addWidget(self.firstupVecZL, 6, 0, 1, 1)
        self.firstupVecXSB = QtGui.QSpinBox(self.mainGB)
        self.firstupVecXSB.setObjectName(_fromUtf8("firstupVecXSB"))
        self.gridLayout_2.addWidget(self.firstupVecXSB, 6, 1, 1, 2)
        self.firstupVecYSB = QtGui.QSpinBox(self.mainGB)
        self.firstupVecYSB.setProperty(_fromUtf8("value"), 1)
        self.firstupVecYSB.setObjectName(_fromUtf8("firstupVecYSB"))
        self.gridLayout_2.addWidget(self.firstupVecYSB, 6, 3, 1, 1)
        self.connectMatrixCB = QtGui.QCheckBox(self.mainGB)
        self.connectMatrixCB.setChecked(True)
        self.connectMatrixCB.setObjectName(_fromUtf8("connectMatrixCB"))
        self.gridLayout_2.addWidget(self.connectMatrixCB, 8, 0, 1, 4)
        self.createTargetsCB = QtGui.QCheckBox(self.mainGB)
        self.createTargetsCB.setObjectName(_fromUtf8("createTargetsCB"))
        self.gridLayout_2.addWidget(self.createTargetsCB, 9, 0, 1, 3)
        self.targetsL = QtGui.QLabel(self.mainGB)
        self.targetsL.setObjectName(_fromUtf8("targetsL"))
        self.gridLayout_2.addWidget(self.targetsL, 10, 0, 1, 1)
        self.targetsPB = QtGui.QPushButton(self.mainGB)
        self.targetsPB.setObjectName(_fromUtf8("targetsPB"))
        self.gridLayout_2.addWidget(self.targetsPB, 10, 1, 1, 3)
        self.targetsLW = QtGui.QListWidget(self.mainGB)
        self.targetsLW.setObjectName(_fromUtf8("targetsLW"))
        self.gridLayout_2.addWidget(self.targetsLW, 11, 0, 1, 7)
        self.createPB = QtGui.QPushButton(self.mainGB)
        self.createPB.setObjectName(_fromUtf8("createPB"))
        self.gridLayout_2.addWidget(self.createPB, 12, 0, 1, 7)
        self.firstupVecZSB = QtGui.QSpinBox(self.mainGB)
        self.firstupVecZSB.setObjectName(_fromUtf8("firstupVecZSB"))
        self.gridLayout_2.addWidget(self.firstupVecZSB, 6, 4, 1, 1)
        self.makeLiveVectorCB = QtGui.QCheckBox(self.mainGB)
        self.makeLiveVectorCB.setChecked(True)
        self.makeLiveVectorCB.setObjectName(_fromUtf8("makeLiveVectorCB"))
        self.gridLayout_2.addWidget(self.makeLiveVectorCB, 7, 0, 1, 2)
        self.gridLayout.addWidget(self.mainGB, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.mainGB.setTitle(QtGui.QApplication.translate("Form", "MG_splinePath Ui V 1.00", None, QtGui.QApplication.UnicodeUTF8))
        self.baseNameL.setText(QtGui.QApplication.translate("Form", "baseName :", None, QtGui.QApplication.UnicodeUTF8))
        self.sideL.setText(QtGui.QApplication.translate("Form", "side  :", None, QtGui.QApplication.UnicodeUTF8))
        self.samplesL.setText(QtGui.QApplication.translate("Form", "Number of sample :", None, QtGui.QApplication.UnicodeUTF8))
        self.outputsL.setText(QtGui.QApplication.translate("Form", "Number of output:", None, QtGui.QApplication.UnicodeUTF8))
        self.offsetL.setText(QtGui.QApplication.translate("Form", "Offset:", None, QtGui.QApplication.UnicodeUTF8))
        self.inputCurveL.setText(QtGui.QApplication.translate("Form", "Input Curve :", None, QtGui.QApplication.UnicodeUTF8))
        self.inputCurvePB.setText(QtGui.QApplication.translate("Form", "LOAD", None, QtGui.QApplication.UnicodeUTF8))
        self.firstupVecZL.setText(QtGui.QApplication.translate("Form", "First upVec :", None, QtGui.QApplication.UnicodeUTF8))
        self.connectMatrixCB.setText(QtGui.QApplication.translate("Form", "connect parentMatrix", None, QtGui.QApplication.UnicodeUTF8))
        self.createTargetsCB.setText(QtGui.QApplication.translate("Form", "Create Targets", None, QtGui.QApplication.UnicodeUTF8))
        self.targetsL.setText(QtGui.QApplication.translate("Form", "Targets :", None, QtGui.QApplication.UnicodeUTF8))
        self.targetsPB.setText(QtGui.QApplication.translate("Form", "LOAD", None, QtGui.QApplication.UnicodeUTF8))
        self.createPB.setText(QtGui.QApplication.translate("Form", "CREATE", None, QtGui.QApplication.UnicodeUTF8))
        self.makeLiveVectorCB.setText(QtGui.QApplication.translate("Form", "make live vector", None, QtGui.QApplication.UnicodeUTF8))
        self.customUi()
    
    def customUi(self):
        '''
        This procedure runs all the customizzation and overridings on the main ui
        '''
        self.connect(self.inputCurvePB,QtCore.SIGNAL('clicked()'), partial(self.loadEditline, self.inputCurveLE))
        self.connect(self.targetsPB,QtCore.SIGNAL('clicked()'), partial(self.loadListView, self.targetsLW))
        self.connect(self.createTargetsCB,QtCore.SIGNAL('clicked()'), self.__disableListW)
        self.connect(self.createPB,QtCore.SIGNAL('clicked()'), self.__create)
    def __disableListW(self):
        if self.createTargetsCB.isChecked() == 1 :
            self.targetsLW.setEnabled(0)
        else :
            self.targetsLW.setEnabled(1)


    def __create(self):
        baseName = str ( self.baseNameLE.text ( ) ) 
        side = str ( self.sideLE.text ( ) ) 
        numberOfSamples = int ( self.samplesSB.value() )
        numberOfOutput = int ( self.outputsSB.value() )
        offset = int ( self.offsetSB.value() )
        inputCurve = str ( self.inputCurveLE.text ( ) ) 
        firstUpVec = [ self.firstupVecXSB.value() , self.firstupVecYSB.value() , self.firstupVecZSB.value()]
        connectParentMatrix = int(self.connectMatrixCB.isChecked())
        createTargets = int(self.createTargetsCB.isChecked())
        targets = self.getListViewObjects(self.targetsLW)
        makeLiveVector = self.makeLiveVectorCB.isChecked()

        
        spline = MG_splinePath.MG_splinePath(baseName = baseName , side = side ,
                                        numberOfSamples = numberOfSamples , numberOfOutputs = numberOfOutput 
                                        , inputCurve = inputCurve , targets = targets , offset = offset , 
                                        createTargets = createTargets , firstUpVec = firstUpVec ,
                                        connectParentMatrix = connectParentMatrix , makeLiveUpVector = makeLiveVector)
        
        spline.create()
        
        
        
    def loadEditline  ( self , widget ) :
        '''
        @brief          This procedure let you load the current selection into a lineEdit widget , only load the first item of the selection
        @param[in] layout :  this is the widget we need to load the selection on
        '''
        selection = cmds.ls ( sl = 1 ) [ 0 ] 
        widget.setText(selection)

    def loadListView ( self , widget ) :
        '''
        @brief          This procedure let you load the current selection into a listView widget
        @param[in] layout :  this is the widget we need to load the selection on
        '''
        widget.clear()
        selection = cmds.ls ( sl = 1 )
        for i in selection :
            widget.addItem (i)

    def getListViewObjects (self , widget ):
        
        objList = []
        for i in range(widget.count()):
            objList.append(str(widget.item(i).text()))
            
        return objList
    
def getMayaWindow():
    '''
    @brief         standard procedure used to get current Maya window (not for the users)
    '''
    ptr = apiUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class MG_splinePathGUI(QtGui.QWidget, Ui_Form):
    '''
    @brief         this is the wrap class around our main widget , this is the class that gets instantiated and loaded
    '''
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent=getMayaWindow())
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.setupUi(self)

def show():
    ui=MG_splinePathGUI()
    ui.show()