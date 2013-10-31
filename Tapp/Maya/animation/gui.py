import os
import webbrowser

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

import Tapp.Maya.animation.character as character
reload(character)
import Tapp.Maya.utils.ZvParentMaster as muz
reload(muz)
import Tapp.Maya.animation.utils as mau
reload(mau)
import Tapp.Maya.animation.utils.ml_breakdownDragger as maumlb
reload(maumlb)
import Tapp.Maya.animation.utils.ml_hold as maumlh
reload(maumlh)
import Tapp.Maya.animation.utils.ml_keyValueDragger as maumlk
reload(maumlk)
import Tapp.Maya.utils.paie as paie
reload(paie)
import Tapp.Maya.animation.resources.animation as gui
reload(gui)
import Tapp.Maya.rigging.meta as meta
reload(meta)

'''
import Tapp.utils.pyside.compileUi as upc
#uiPath=os.path.dirname(__file__)+'/resources/timing.ui'
uiPath=r'C:\Users\toke.jepsen\Documents\GitHub\Tapp\Tapp\Maya\animation\resources\animation.ui'
upc.compileUi(uiPath)
'''


def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class Window(QtGui.QMainWindow,gui.Ui_MainWindow):
    
    def __init__(self, parent=maya_main_window()):
        super(Window,self).__init__(parent)
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
        #self.character_keylimb_pushButton.released.connect(self.on_character_keylimb_pushButton_released)
        #self.character_keycharacter_pushButton.released.connect(self.on_character_keycharacter_pushButton_released)
        #self.character_selectlimb_pushButton.released.connect(self.on_character_selectlimb_pushButton_released)
        #self.character_selectcharacter_pushButton.released.connect(self.on_character_selectcharacter_pushButton_released)
        
        self.character_range_checkBox.stateChanged.connect(self.character_range)
        self.character_start_pushButton.released.connect(self.character_start)
        self.character_end_pushButton.released.connect(self.character_end)
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
        
        self.tools_localizeImagePlane_pushButton.released.connect(self.on_localizeImagePlane_pushButton_released)
        
        self.tools_rat_pushButton.released.connect(self.on_tools_rat_pushButton_released)
        
        self.tools_paie_pushButton.released.connect(self.tools_paie)
    
    def on_localizeImagePlane_pushButton_released(self):
        
        import Tapp.Maya.animation.utils.imageplane as ip
        
        ip.localizeImagePlane()
    
    def tools_paie(self):
        
        paie.GUI()
    
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
            
            character.switch('IK',timeRange=True, start=start, end=end)
            
        else:
            character.switch('IK')
    
    def on_character_fk_pushButton_released(self):
        
        if self.character_range_checkBox.checkState()==QtCore.Qt.CheckState.Checked:
            
            start=int(float(self.character_start_lineEdit.text()))
            end=int(float(self.character_end_lineEdit.text()))
            
            character.switch('FK',timeRange=True, start=start, end=end)
            
        else:
            character.switch('FK')
    
    def on_character_zerocontrol_pushButton_released(self):
        
        #undo enable
        cmds.undoInfo(openChunk=True)
        
        #getting selection
        sel=cmds.ls(sl=True)
        
        #zero controls
        if len(sel)>=1:
            for node in cmds.ls(sl=True):
                character.zeroNode(node)
            
            #revert selection
            cmds.select(sel)
        else:
            cmds.warning('No nodes select!')
        
        cmds.undoInfo(closeChunk=True)
    
    def on_character_zerolimb_pushButton_released(self):
        
        '''
        #undo enable
        cmds.undoInfo(openChunk=True)
        
        #getting selection
        sel=cmds.ls(sl=True)
        
        #zero controls
        if len(sel)>=1:
            
            roots=[]
            for node in sel:
                mNode=meta.r9Meta.MetaClass(node).getParentMetaNode()
                
                roots.append(meta.r9Meta.getConnectedMetaSystemRoot(mNode.mNode))
            
            def recurseListConnections(node,attr,result=[]):
                
                children=cmds.listConnections(node.mNode+'.'+attr)
                
                if children:
                    for child in children:
                        result.append(child)
            
            for root in list(set(roots)):
                
                recurseListConnections(root,'points')
                
                #for control in root.getChildControls():
                #    character.zeroNode(control.getNode())
            
            #revert selection
            cmds.select(sel)
        else:
            cmds.warning('No nodes select!')
        
        cmds.undoInfo(closeChunk=True)
        '''
    
    def on_character_zerocharacter_pushButton_released(self):
        
        print 'zero character'
    
    def on_character_keylimb_pushButton_released(self):
        
        pass
    
    def on_character_keycharacter_pushButton_released(self):
        
        pass
    
    def on_character_selectlimb_pushButton_released(self):
        
        pass
    
    def on_character_selectcharacter_pushButton_released(self):
        
        pass
    
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

def show():
    #showing new dialog
    win=Window()
    win.show()

win=Window()
win.on_character_zerolimb_pushButton_released()