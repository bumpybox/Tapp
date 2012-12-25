'''
more procedural gui build > defining types should be enough
editing existing meta data
more fail safes defining the types of objects for each meta object
'''

from PyQt4 import QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

from bbt_maya import generic

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class tagDialog(QtGui.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        
        self.setObjectName('tagDialog')
        self.setWindowTitle('Tagger')
        
        self.types={}
        self.types['root']={'node':'meta_root','component':'character','version':'1.0.1','characterName':'Character Name'}
        self.types['module']={'node':'meta_module','component':'finger','index':'1','side':['r','c','l'],
                              'system':['template','animation']}
        self.types['control']={'component':'joint','system':['None','fk','ik'],'worldspace':['true','false'],
                               'switch':'message','metaParent':'metaParent'}
        self.types['skin']={'component':'geometry'}
        self.types['proxy']={}
        self.types['camera']={'component':['face','animation']}
        self.types['socket']={'index':'1,2,3,4','metaParent':'Meta Parent'}
        self.types['plug']={'metaParent':'Meta Parent'}
        self.types['joint']={'component':'neck','metaParent':'metaParent'}
        
        self.createLayout()
        self.createConnections()
    
    def createLayout(self):
        ''' Creates initial layout '''
        
        #initial layout
        self.main_layout = QtGui.QVBoxLayout()
        label=QtGui.QLabel('Choose the type of object.')
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        
        self.typeCBox=QtGui.QComboBox()
        for item in self.types:
            self.typeCBox.addItem(item)
        
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(self.typeCBox)
        
        self.inputWidget=QtGui.QWidget()
        self.setLayout(self.main_layout)
        
        self.tagButton=QtGui.QPushButton('Tag IT!')
        self.main_layout.addWidget(self.tagButton)
        
        self.setInputData('control')
    
    def setInputData(self,inputType):
        ''' Generates input data fields.'''
        
        #layout
        self.inputWidget.close()
        self.inputWidget=QtGui.QWidget()
        self.inputLayout=QtGui.QGridLayout()
        self.inputWidget.setLayout(self.inputLayout)
        
        #generate inputs
        rowCount=0
        for item in self.types[inputType]:
            
            #if string value then line edit input
            if isinstance(self.types[inputType][item], str):
                label=QtGui.QLabel(item)
                lineInput=QtGui.QLineEdit(self.types[inputType][item])
    
                self.inputLayout.addWidget(label,rowCount,0)
                self.inputLayout.addWidget(lineInput,rowCount,1)
            
            #if list value then combobox
            if isinstance(self.types[inputType][item], list):
                label=QtGui.QLabel(item)
                comboBox=QtGui.QComboBox()
                comboBox.addItems(self.types[inputType][item])
    
                self.inputLayout.addWidget(label,rowCount,0)
                self.inputLayout.addWidget(comboBox,rowCount,1)
            
            rowCount+=1
        
        self.main_layout.addWidget(self.inputWidget)

    def getInputData(self):
        ''' Returns all input data as dictionary '''
        
        data={}
        
        #loops through the input layouts children and append to data dictionary
        for count in range(0,self.inputLayout.count(),2):
            label=self.inputLayout.itemAt(count).widget()
            inputWdg=self.inputLayout.itemAt(count+1).widget()
            
            if type(inputWdg)==QtGui.QComboBox:
                data[str(label.text())]=str(inputWdg.currentText())
            if type(inputWdg)==QtGui.QLineEdit:
                data[str(label.text())]=str(inputWdg.text())
        
        return data
    
    def createConnections(self):
        self.connect(self.typeCBox, QtCore.SIGNAL('currentIndexChanged(int)'),self.typeChoice)
        
        self.connect(self.tagButton, QtCore.SIGNAL('clicked()'),self.tagIT)
    
    def tagIT(self):
        if self.typeCBox.currentText()=='camera':
            #making sure something is selected
            sel=cmds.ls(selection=True)
            
            if len(sel)<1:
                cmds.warning('No object selected.')
            elif cmds.nodeType(cmds.listRelatives(sel[0])[0])!='camera':
                cmds.warning('Selection is not a camera.')
            else:
                data=self.getInputData()
                component=data['component']
                del(data['component'])
                
                meta=generic.Meta()
                
                node=sel[0]
                
                metaParent=meta.SetData(('meta_'+node), 'camera', component, None,None)
                
                cmds.addAttr(node,longName='metaParent',attributeType='message')
                cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
        
        if self.typeCBox.currentText()=='joint':
            #making sure something is selected
            sel=cmds.ls(selection=True)
            
            if len(sel)<1:
                cmds.warning('No joint object selected.')
            else:
                data=self.getInputData()
                component=data['component']
                del(data['component'])
                metaNode=data['metaParent']
                del(data['metaParent'])
                
                data['system']='skin'
                
                meta=generic.Meta()
                
                for node in sel:
                    metaParent=meta.SetData(('meta_'+node), 'joint', component, metaNode,data)
                    
                    cmds.addAttr(node,longName='metaParent',attributeType='message')
                    cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
        
        if self.typeCBox.currentText()=='socket':
            #making sure something is selected
            sel=cmds.ls(selection=True)
            
            if len(sel)<1:
                cmds.warning('No socket object selected.')
            else:
                data=self.getInputData()
                
                #separating required data out               
                module=data['metaParent']
                del(data['metaParent'])
                
                #creating socket
                meta=generic.Meta()
                
                node=sel[0]
                
                metaParent=meta.SetData(('meta_'+node), 'socket', None, module,data)
                
                if cmds.attributeQuery('metaParent',n=node,ex=True)==False:
                    cmds.addAttr(node,longName='metaParent',attributeType='message')
                    cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
                else:
                    cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
        
        if self.typeCBox.currentText()=='plug':
            #making sure something is selected
            sel=cmds.ls(selection=True)
            
            if len(sel)<1:
                cmds.warning('No plug object selected.')
            else:
                data=self.getInputData()
                
                #separating required data out               
                module=data['metaParent']
                del(data['metaParent'])
                
                #creating socket
                meta=generic.Meta()
                
                node=sel[0]
                
                metaParent=meta.SetData(('meta_'+node), 'plug', None, module,data)
                
                if cmds.attributeQuery('metaParent',n=node,ex=True)==False:
                    cmds.addAttr(node,longName='metaParent',attributeType='message')
                    cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
                else:
                    cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
        
        if self.typeCBox.currentText()=='root':
            data=self.getInputData()
            
            meta=generic.Meta()
            
            meta.createRoot(data['node'], data['version'], data['component'],data['characterName'])
        
        if self.typeCBox.currentText()=='module':
            data=self.getInputData()
            
            #separating required data out
            node=data['node']
            del(data['node'])
            
            component=data['component']
            del(data['component'])
            
            #creating module
            meta=generic.Meta()
            
            meta.SetData(node, 'module', component, None,data)
            
        if self.typeCBox.currentText()=='control':
            #making sure something is selected
            sel=cmds.ls(selection=True)
            
            if len(sel)<1:
                cmds.warning('No control object selected.')
            else:
                data=self.getInputData()
                
                #removing component from data dict
                component=data['component']
                del(data['component'])
                module=data['metaParent']
                del(data['metaParent'])
                
                meta=generic.Meta()
                
                for node in sel:
                    metaParent=meta.SetData(('meta_'+node),'control', component, module,None)
                    
                    cmds.addAttr(node,longName='metaParent',attributeType='message')
                    cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
        
        if self.typeCBox.currentText()=='proxy':
            #making sure something is selected
            sel=cmds.ls(selection=True)
            
            if len(sel)<1:
                cmds.warning('No proxy object selected.')
            else:
                meta=generic.Meta()
                
                for node in sel:
                    metaParent=meta.createProxy(('meta_'+node))
                    
                    if cmds.attributeQuery('metaParent',n=node,ex=True)==False:
                        cmds.addAttr(node,longName='metaParent',attributeType='message')
                        cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
                    else:
                        cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)

        if self.typeCBox.currentText()=='skin':
            #making sure something is selected
            sel=cmds.ls(selection=True)
            
            if len(sel)<1:
                cmds.warning('No skin object selected.')
            else:
                meta=generic.Meta()
                
                for node in sel:
                    metaParent=meta.createSkin(('meta_'+node))
                    
                    if cmds.attributeQuery('metaParent',n=node,ex=True)==False:
                        cmds.addAttr(node,longName='metaParent',attributeType='message')
                        cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
                    else:
                        cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
    
    def typeChoice(self):
        if self.typeCBox.currentText()=='socket':
            self.setInputData('socket')
        
        if self.typeCBox.currentText()=='plug':
            self.setInputData('plug')
        
        if self.typeCBox.currentText()=='proxy':
            self.setInputData('proxy')
        
        if self.typeCBox.currentText()=='skin':
            self.setInputData('skin')
        
        if self.typeCBox.currentText()=='control':
            self.setInputData('control')
        
        if self.typeCBox.currentText()=='root':
            self.setInputData('root')
           
        if self.typeCBox.currentText()=='module':
            self.setInputData('module')
        
        if self.typeCBox.currentText()=='joint':
            self.setInputData('joint')
        
        if self.typeCBox.currentText()=='camera':
            self.setInputData('camera')

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tagDialog':
            widget.close()
    
    #showing new dialog
    win=tagDialog()
    win.show()

show()