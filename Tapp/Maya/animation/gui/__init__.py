import os
import webbrowser
import xml.etree.ElementTree as xml
from cStringIO import StringIO

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu

import shiboken
import pysideuic
from PySide import QtGui, QtCore

import Tapp.Maya.animation.character as character
reload(character)
import Tapp.Maya.animation.tools as tools
import Tapp.Maya.utils.ZvParentMaster as muz
import Tapp.Maya.animation.utils as mau
import Tapp.Maya.animation.utils.ml_breakdownDragger as maumlb
import Tapp.Maya.animation.utils.ml_hold as maumlh
import Tapp.Maya.animation.utils.ml_keyValueDragger as maumlk

def maya_main_window():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the top level Maya windows
    """
    ptr = omu.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)


def loadUiType(uiFile):
    """
    Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
    and then execute it in a special frame to retrieve the form_class.
    """
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        pysideuic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        #Fetch the base_class and form class based on their type in the xml from designer
        form_class = frame['Ui_%s'%form_class]
        base_class = eval('QtGui.%s'%widget_class)
    return form_class, base_class

uiPath=os.path.dirname(__file__)+'/resources/animation.ui'
uiPath=r'C:\Users\toke.jepsen\Documents\GitHub\Tapp\Tapp\Maya\animation\gui\resources/animation.ui'
form,base=loadUiType(uiPath)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(Form,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tatDialog')
        
        self.create_connections()
        
        self.character_start_pushButton.setEnabled(False)
        self.character_end_pushButton.setEnabled(False)
        
        self.character_start_lineEdit.setReadOnly(False)
        self.character_start_lineEdit.setReadOnly(False)
        
        self.character_start_lineEdit.setEnabled(False)
        self.character_end_lineEdit.setEnabled(False)
    
    def create_connections(self):
        
        #character---
        self.character_ik_pushButton.released.connect(self.on_character_ik_pushButton_released)
        self.character_fk_pushButton.released.connect(self.on_character_fk_pushButton_released)
        self.character_zerocontrol_pushButton.released.connect(self.on_character_zerocontrol_pushButton_released)
        self.character_zerolimb_pushButton.released.connect(self.on_character_zerolimb_pushButton_released)
        self.character_zerocharacter_pushButton.released.connect(self.on_character_zerocharacter_pushButton_released)
        self.character_keylimb_pushButton.released.connect(self.on_character_keylimb_pushButton_released)
        self.character_keycharacter_pushButton.released.connect(self.on_character_keycharacter_pushButton_released)
        self.character_selectlimb_pushButton.released.connect(self.on_character_selectlimb_pushButton_released)
        self.character_selectcharacter_pushButton.released.connect(self.on_character_selectcharacter_pushButton_released)
        
        self.character_range_checkBox.stateChanged.connect(self.character_range)
        self.character_start_pushButton.released.connect(self.character_start)
        self.character_getTimeline_pushButton.released.connect(self.character_timeline)
        
        #tools---
        self.tools_zvparentmaster_pushButton.released.connect(self.on_tools_zvparentmaster_pushButton_released)
        self.tools_zvparentmasterhelp_pushButton.released.connect(self.on_tools_zvparentmasterhelp_pushButton_released)
        self.tools_breakdowndragger_pushButton.released.connect(self.on_tools_breakdowndragger_pushButton_released)
        self.tools_breakdowndraggerhelp_pushButton.released.connect(self.on_tools_breakdowndraggerhelp_pushButton_released)
        self.tools_holdkey_pushButton.released.connect(self.on_tools_holdkey_pushButton_released)
        self.tools_holdkeyhelp_pushButton.released.connect(self.on_tools_holdkeyhelp_pushButton_released)
        self.tools_keyvaluedragger_pushButton.released.connect(self.on_tools_keyvaluedragger_pushButton_released)
        self.tools_keyvaluedraggerhelp_pushButton.released.connect(self.on_tools_keyvaluedraggerhelp_pushButton_released)
        self.tools_keycleanup_pushButton.released.connect(self.on_tools_keycleanup_pushButton_released)
        self.tools_keycleanuphelp_pushButton.released.connect(self.on_tools_keycleanuphelp_pushButton_released)
        self.tools_changeRotationOrder_pushButton.released.connect(self.on_tools_changeRotationOrder_pushButton_released)
        self.tools_changeRotationOrderHelp_pushButton.released.connect(self.on_tools_changeRotationOrderHelp_pushButton_released)
        self.tools_ghosting_pushButton.released.connect(self.on_tools_ghosting_pushButton_released)
        self.tools_ghostingHelp_pushButton.released.connect(self.on_tools_ghostingHelp_pushButton_released)
        self.tools_rat_pushButton.released.connect(self.on_tools_rat_pushButton_released)
        self.tools_importMayaFile_pushButton.released.connect(self.on_tools_importMayaFile_pushButton_released)
    
    def character_range(self):
        
        if self.character_range_checkBox.checkState()==QtCore.Qt.CheckState.Checked:
            self.character_start_pushButton.setEnabled(True)
            self.character_end_pushButton.setEnabled(True)
            
            self.character_start_lineEdit.setEnabled(True)
            self.character_end_lineEdit.setEnabled(True)
        
        if self.character_range_checkBox.checkState()==QtCore.Qt.CheckState.Unchecked:
            self.character_start_pushButton.setEnabled(False)
            self.character_end_pushButton.setEnabled(False)
            
            self.character_start_lineEdit.setEnabled(False)
            self.character_end_lineEdit.setEnabled(False)
            
            self.character_start_lineEdit.clear()
            self.character_end_lineEdit.clear()
    
    def character_start(self):
        
        t=cmds.currentTime(q=True)
        self.character_start_lineEdit.setText(str(t))
    
    def character_end(self):
        
        t=cmds.currentTime(q=True)
        self.character_end_lineEdit.setText(str(t))
    
    def character_timeline(self):
        
        minT=cmds.playbackOptions(q=True,min=True)
        maxT=cmds.playbackOptions(q=True,max=True)
        
        self.character_start_lineEdit.setText(str(minT))
        self.character_end_lineEdit.setText(str(maxT))
    
    def on_character_ik_pushButton_released(self):
        
        if self.character_range_checkBox.checkState()==QtCore.Qt.CheckState.Checked:
            
            start=int(float(self.character_start_lineEdit.text()))
            end=int(float(self.character_end_lineEdit.text()))
            
            character.switch('ik',timeRange=True, start=start, end=end)
            
        else:
            character.switch('ik')
    
    def on_character_fk_pushButton_released(self):
        
        if self.character_range_checkBox.checkState()==QtCore.Qt.CheckState.Checked:
            
            start=int(float(self.character_start_lineEdit.text()))
            end=int(float(self.character_end_lineEdit.text()))
            
            character.switch('fk',timeRange=True, start=start, end=end)
            
        else:
            character.switch('fk')
    
    def on_character_zerocontrol_pushButton_released(self):
        
        character.ZeroControl()
    
    def on_character_zerolimb_pushButton_released(self):
        
        character.ZeroLimb()
    
    def on_character_zerocharacter_pushButton_released(self):
        
        character.ZeroCharacter()
    
    def on_character_keylimb_pushButton_released(self):
        
        character.KeyLimb()
    
    def on_character_keycharacter_pushButton_released(self):
        
        character.KeyCharacter()
    
    def on_character_selectlimb_pushButton_released(self):
        
        character.SelectLimb()
    
    def on_character_selectcharacter_pushButton_released(self):
        
        character.SelectCharacter()
    
    def on_tools_zvparentmaster_pushButton_released(self):
        
        muz.ZvParentMaster()
    
    def on_tools_zvparentmasterhelp_pushButton_released(self):
        
        webbrowser.open('http://www.creativecrash.com/maya/script/zv-parent-master')
    
    def on_tools_breakdowndragger_pushButton_released(self):
        
        maumlb.drag()
    
    def on_tools_breakdowndraggerhelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_breakdownDragger')
    
    def on_tools_holdkey_pushButton_released(self):
        
        maumlh.ui()
    
    def on_tools_holdkeyhelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_hold')
    
    def on_tools_keyvaluedragger_pushButton_released(self):
        
        maumlk.drag()
    
    def on_tools_keyvaluedraggerhelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_keyValueDragger')
    
    def on_tools_keycleanup_pushButton_released(self):
        
        cmds.undoInfo(openChunk=True)
        
        #execute redundant keys script
        path=os.path.dirname(mau.__file__).replace('\\','/')
        
        mel.eval('source "'+path+'/deleteRedundantKeys.mel"')
        mel.eval('llDeleteRedundantKeys;')
        
        #deleting static channels in scene or on selected object
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            cmds.delete(staticChannels=True)
        else:
            cmds.delete(staticChannels=True,all=True)
        
        cmds.undoInfo(closeChunk=True)
    
    def on_tools_keycleanuphelp_pushButton_released(self):
        
        msg='This cleans any static channels and redundant keys.\n'
        msg+='If nothing is selected, everything in the scene gets cleaned.'
        
        cmds.confirmDialog( title='Key Clean Up Info', message=msg,defaultButton='OK')
    
    def on_tools_exportanimation_pushButton_released(self):
        
        tools.ExportAnim()
    
    def on_tools_exportanimationhelp_pushButton_released(self):
        
        pass
    
    def on_tools_importanimation_pushButton_released(self):
        
        tools.ImportAnim()
    
    def on_tools_importanimationhelp_pushButton_released(self):
        
        pass
    
    def on_tools_changeRotationOrder_pushButton_released(self):
        
        path=os.path.dirname(__file__)
        parentDir=os.path.abspath(os.path.join(path, os.pardir))
        
        #sourcing zoo utils
        melPath=parentDir+'/utils/zooUtils.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        #sourcing zoo change
        melPath=parentDir+'/utils/zooChangeRoo.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        mel.eval('zooChangeRoo %s' % self.tools_changeRotationOrder_comboBox.currentText())
    
    def on_tools_changeRotationOrderHelp_pushButton_released(self):
        
        webbrowser.open('http://www.creativecrash.com/maya/script/zoochangeroo')
    
    def on_tools_ghosting_pushButton_released(self):
        
        path=os.path.dirname(__file__)
        parentDir=os.path.abspath(os.path.join(path, os.pardir))
        
        #sourcing ghost util
        melPath=parentDir+'/utils/bhGhost.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        mel.eval('bhGhost')
    
    def on_tools_ghostingHelp_pushButton_released(self):
        
        webbrowser.open('https://vimeo.com/50029607')
    
    def on_tools_rat_pushButton_released(self):
        
        path=os.path.dirname(__file__)
        parentDir=os.path.abspath(os.path.join(path, os.pardir))
        
        #sourcing rat util
        melPath=parentDir+'/utils/RAT.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        #launching rat gui
        uiPath=parentDir+'/utils/RAT_ui.ui'
        uiPath=uiPath.replace('\\','/')
        mel.eval('RAT_GUI(1,"%s")' % uiPath)
    
    def on_tools_importMayaFile_pushButton_released(self):
        
        workspace=cmds.workspace( q=True, dir=True )
        workspace=os.path.abspath(os.path.join(workspace, os.pardir))
        workspace=os.path.abspath(os.path.join(workspace, os.pardir))
        workspace=os.path.join(workspace,'publish')
        
        #getting file path and name
        basicFilter = "MAYA (*.ma)"
        filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                                  fileMode=1,startingDirectory=workspace,
                                  caption='Import Maya File')
        
        if filePath!=None:
            
            #replace reference
            cmds.file(filePath,i=True,namespace=':')
            
            #setting timeline
            lastKey=int(cmds.findKeyframe( 'grandpa:c_spine1_master_cnt', which="last" ))
            firstKey=cmds.findKeyframe( 'grandpa:c_spine1_master_cnt', which="first" )
            
            cmds.playbackOptions(min=firstKey)
            cmds.playbackOptions(max=lastKey)
            
            cmds.playbackOptions(ast=firstKey)
            cmds.playbackOptions(aet=lastKey)
            
            #final notification
            cmds.confirmDialog( title='FINISHED', message='mocap imported')

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tatDialog':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()