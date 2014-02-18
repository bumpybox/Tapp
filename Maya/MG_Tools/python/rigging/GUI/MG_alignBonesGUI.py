from PyQt4 import QtCore, QtGui

import sip 
import maya.OpenMayaUI as apiUI
from maya import cmds , OpenMaya

import MG_Tools.python.rigging.script.MG_alignBones as MG_alignBones
reload(MG_alignBones)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(278, 409)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupUI = QtGui.QGroupBox(Form)
        self.groupUI.setTitle(_fromUtf8(""))
        self.groupUI.setObjectName(_fromUtf8("groupUI"))
        self.gridLayout = QtGui.QGridLayout(self.groupUI)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.bonesLW = QtGui.QListWidget(self.groupUI)
        self.bonesLW.setObjectName(_fromUtf8("bonesLW"))
        self.gridLayout.addWidget(self.bonesLW, 0, 0, 1, 1)
        self.loadPB = QtGui.QPushButton(self.groupUI)
        self.loadPB.setObjectName(_fromUtf8("loadPB"))
        self.gridLayout.addWidget(self.loadPB, 1, 0, 1, 1)
        self.hierCB = QtGui.QCheckBox(self.groupUI)
        self.hierCB.setObjectName(_fromUtf8("hierCB"))
        self.gridLayout.addWidget(self.hierCB, 2, 0, 1, 1)
        self.reverseCB = QtGui.QCheckBox(self.groupUI)
        self.reverseCB.setObjectName(_fromUtf8("reverseCB"))
        self.gridLayout.addWidget(self.reverseCB, 3, 0, 1, 1)
        self.modeTB = QtGui.QToolBox(self.groupUI)
        self.modeTB.setMinimumSize(QtCore.QSize(140, 140))
        self.modeTB.setObjectName(_fromUtf8("modeTB"))
        self.virtualP = QtGui.QWidget()
        self.virtualP.setGeometry(QtCore.QRect(0, 0, 240, 86))
        self.virtualP.setObjectName(_fromUtf8("virtualP"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.virtualP)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.orientVirtualPB = QtGui.QPushButton(self.virtualP)
        self.orientVirtualPB.setObjectName(_fromUtf8("orientVirtualPB"))
        self.verticalLayout_2.addWidget(self.orientVirtualPB)
        self.modeTB.addItem(self.virtualP, _fromUtf8(""))
        self.geometryP = QtGui.QWidget()
        self.geometryP.setGeometry(QtCore.QRect(0, 0, 240, 86))
        self.geometryP.setObjectName(_fromUtf8("geometryP"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.geometryP)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.initPB = QtGui.QPushButton(self.geometryP)
        self.initPB.setObjectName(_fromUtf8("initPB"))
        self.verticalLayout_3.addWidget(self.initPB)
        self.orientGeoPB = QtGui.QPushButton(self.geometryP)
        self.orientGeoPB.setObjectName(_fromUtf8("orientGeoPB"))
        self.verticalLayout_3.addWidget(self.orientGeoPB)
        self.modeTB.addItem(self.geometryP, _fromUtf8(""))
        self.gridLayout.addWidget(self.modeTB, 4, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupUI)

        self.retranslateUi(Form)
        self.modeTB.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "MG_alignBones V1.00", None, QtGui.QApplication.UnicodeUTF8))
        self.loadPB.setText(QtGui.QApplication.translate("Form", "LOAD BONES", None, QtGui.QApplication.UnicodeUTF8))
        self.hierCB.setText(QtGui.QApplication.translate("Form", "Hierarchy", None, QtGui.QApplication.UnicodeUTF8))
        self.reverseCB.setText(QtGui.QApplication.translate("Form", "Reverse Normal", None, QtGui.QApplication.UnicodeUTF8))
        self.orientVirtualPB.setText(QtGui.QApplication.translate("Form", "ORIENT BONES", None, QtGui.QApplication.UnicodeUTF8))
        self.modeTB.setItemText(self.modeTB.indexOf(self.virtualP), QtGui.QApplication.translate("Form", "Virtual Plane", None, QtGui.QApplication.UnicodeUTF8))
        self.initPB.setText(QtGui.QApplication.translate("Form", "INIT GEOMETRY", None, QtGui.QApplication.UnicodeUTF8))
        self.orientGeoPB.setText(QtGui.QApplication.translate("Form", "ORIENT BONES", None, QtGui.QApplication.UnicodeUTF8))
        self.modeTB.setItemText(self.modeTB.indexOf(self.geometryP), QtGui.QApplication.translate("Form", "Geometry Plane", None, QtGui.QApplication.UnicodeUTF8))

        self.customUi()
    
    def customUi(self):
        '''
        This procedure runs all the customizzation and overridings on the main ui
        '''
        #vars
        self.bones = []
        self.hierarchy = 0
        self.reverseNormal = 0
        self.tempClass = None
        
        
        #connects
        self.connect( self.loadPB , QtCore.SIGNAL('clicked()') , self.loadBones )
        self.connect( self.orientVirtualPB , QtCore.SIGNAL('clicked()') , self.alignVirtual )
        self.connect( self.initPB , QtCore.SIGNAL('clicked()') , self.initGeometry )
        self.connect( self.orientGeoPB , QtCore.SIGNAL('clicked()') , self.orientGeometry )
    def loadBones(self):
        '''
        This procedure loads the select bones in the list widget
        '''
        sel = cmds.ls(sl = 1 )
        
        for s in sel :
            if cmds.nodeType(s) != "joint" : 
                OpenMaya.MGlobal.displayError("Please select bones only")
                return
        self.bonesLW.clear()
        self.bonesLW.addItems(sel)    
    
    def __getUiData(self):
        '''
        This private procedure is in charge of getting all the meaningful data form
        the UI
        '''
        self.bones =[]
        for i in range(self.bonesLW.count()) :
            self.bones.append(str(self.bonesLW.item(i).text()))
        
        self.hierarchy = self.hierCB.isChecked()
        self.reverseNormal = self.reverseCB.isChecked()
    
    
    def alignVirtual (self):
        '''
        This procedure aligns the bones using the virtual plane method
        '''
        self.__getUiData()
        
        if not self.bones :
            OpenMaya.MGlobal.displayError("No bones loaded to re-orient")
            return
        al = MG_alignBones.MG_alignBones(self.bones)
        al.withVirtualPlane(self.hierarchy , self.reverseNormal)
    
    def initGeometry(self):
        '''
        This procedure inits the geometry for align with geometry mode
        '''
        self.__getUiData()
        
        if not self.bones :
            OpenMaya.MGlobal.displayError("No bones loaded to re-orient")
            return
        self.tempClass = MG_alignBones.MG_alignBones(self.bones)
        self.tempClass.withGeometryPlaneInit()
        
    def orientGeometry(self):
        '''
        This procedure orients the bones using the created plane
        '''
        self.__getUiData()
        if self.tempClass :
            self.tempClass.withGeometryPlaneDoit(self.hierarchy , self.reverseNormal)
    
def getMayaWindow():
    '''
    @brief         standard procedure used to get current Maya window (not for the users)
    '''
    ptr = apiUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class MG_alignBonesGUI(QtGui.QWidget, Ui_Form):
    '''
    @brief         this is the wrap class around our main widget , this is the class that gets instantiated and loaded
    '''
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent=getMayaWindow())
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.setupUi(self)

def show():
    ui=MG_alignBonesGUI()
    ui.show()