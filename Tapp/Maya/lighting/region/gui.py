'''
- non renderlayer selected fail safe
- pass in nodes to find the region on
- error for user when render region because of locked attributes
    - viewport based preview?
'''

from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import Tapp.Maya.lighting.region.resources.region as gui
reload(gui)
import Tapp.Maya.lighting.region.utils as utils
reload(utils)


import Tapp.utils.pyside.compileUi as upc
#uiPath=os.path.dirname(__file__)+'/resources/timing.ui'
uiPath=r'C:\Users\toke.jepsen\Documents\GitHub\Tapp\Tapp\Maya\lighting\region\resources\region.ui'
upc.compileUi(uiPath)

def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class Window(QtGui.QMainWindow,gui.Ui_MainWindow):
    
    def __init__(self, parent=maya_main_window()):
        super(Window,self).__init__(parent)
        self.setupUi(self)
        
        self.mod_layout()
        
        self.create_connections()
    
    def mod_layout(self):
        
        nodes=utils.getRegionNode()
        
        for node in nodes:
            
            renderlayer=cmds.listConnections(node+'.renderlayer')[0]
            self.renderlayer_listWidget.addItem(renderlayer)
    
    def create_connections(self):
        
        self.renderlayer_listWidget.clicked.connect(self.on_renderlayer_clicked)
        
        self.refresh_pushButton.pressed.connect(self.refresh)
        
        self.getPreviewRegion_pushButton.pressed.connect(self.on_getPreviewRegion_pressed)
        
        self.getObjectRegion_pushButton.pressed.connect(self.on_getObjectRegion_pressed)
        
        self.connectArnold_pushButton.pressed.connect(self.on_connectArnold_pressed)
        self.disconnectArnold_pushButton.pressed.connect(self.on_disconnectArnold_pressed)
        
        self.connectPreview_pushButton.pressed.connect(self.on_connectPreview_pressed)
        self.disconnectPreview_pushButton.pressed.connect(self.on_disconnectPreview_pressed)
    
    def getSelectedRegionNode(self):
        
        if self.renderlayer_listWidget.selectedItems():
            renderlayer=self.renderlayer_listWidget.selectedItems()[0].text()
            
            cmds.editRenderLayerGlobals( currentRenderLayer=renderlayer)
            cmds.refresh()
            
            regionNode=cmds.listConnections(renderlayer+'.message',type='network')[0]
            
            return regionNode
        else:
            return None
    
    def on_renderlayer_clicked(self):
        
        renderlayer=self.renderlayer_listWidget.selectedItems()[0].text()
        
        cmds.editRenderLayerGlobals( currentRenderLayer=renderlayer)
        cmds.refresh()
        
        regionNode=cmds.listConnections(renderlayer+'.message',type='network')[0]
        
        cmds.select(regionNode)
    
    def refresh(self):
        
        self.renderlayer_listWidget.clear()
        
        nodes=utils.getRegionNode()
        
        for node in nodes:
            
            renderlayer=cmds.listConnections(node+'.renderlayer')[0]
            self.renderlayer_listWidget.addItem(renderlayer)
    
    def on_getPreviewRegion_pressed(self):
        
        r=utils.getRegionDraw()
        
        regionNode=self.getSelectedRegionNode()
        
        if regionNode:
        
            utils.setRegionNode(regionNode, r)
        
        else:
            
            cmds.warning('No renderlayer selected in region window!')
    
    def on_getObjectRegion_pressed(self):
        
        sel=cmds.ls(selection=True)
        
        #checking selection for meshes
        check=False
        for node in sel:
            
            shape=cmds.listRelatives(node,shapes=True)
            if shape:
                
                if cmds.nodeType(shape)=='mesh':
                    
                    check=True
        
        if check:
        
            regions=utils.getMeshAnimation()
            
            regionNode=self.getSelectedRegionNode()
            
            for r in regions:
                
                utils.setRegionNode(regionNode, r)
        
        else:
            
            cmds.warning('Nothing selected. Please select one or more meshes!')
    
    def on_connectArnold_pressed(self):
        
        utils.connectArnold()
    
    def on_disconnectArnold_pressed(self):
        
        utils.disconnectArnold()
    
    def on_connectPreview_pressed(self):
        
        utils.connectPreview()
    
    def on_disconnectPreview_pressed(self):
        
        utils.disconnectPreview()

win=Window()
win.show()