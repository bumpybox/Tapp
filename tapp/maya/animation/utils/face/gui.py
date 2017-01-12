from PyQt4 import QtCore, QtGui

import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

from bbt_maya.bat.face import utils
from bbt_maya import generic

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class faceDialog(QtGui.QDialog):

    def __init__(self,camera,name,parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        
        self.setObjectName('faceDialog')
        self.setWindowTitle(name+' Face Controls')
        self.resize(QtCore.QSize(500,500))

        self.verticalLayout = QtGui.QVBoxLayout(self)
        # need to set a name so it can be referenced by maya node path
        self.verticalLayout.setObjectName('mainLayout')
        # First use SIP to unwrap the layout into a pointer
        # Then get the full path to the UI in maya as a string
        layout = omu.MQtUtil.fullName(long(sip.unwrapinstance(self.verticalLayout)))
        cmds.setParent(layout)
        
        nodeName = cmds.modelEditor(camera=camera)
        # Find a pointer to the modelPanel that we just created
        ptr = omu.MQtUtil.findControl(nodeName)
        # Wrap the pointer into a python QObject
        self.modelPanel = sip.wrapinstance(long(ptr), QtCore.QObject)
        
        # add our QObject reference to the modelPanel to our layout
        self.verticalLayout.addWidget(self.modelPanel)

def show():
    
    camera=utils.getFaceCam()
    
    if camera!=None:
        meta=generic.Meta()
        rootData=meta.getData(meta.upStream(camera, 'root'))
        
        win=faceDialog(camera,rootData['name'])
        win.show()