from maya import cmds
from MG_Tools.python.anim.script import MG_smallMovement


from maya import  cmds , OpenMaya , mel
from MG_Tools.python.utils import jsonUtils
import os

class MG_smallMovementGUIOld (object):
    '''
     
    @author             Marco Giordano
     
    @date               04.23.2013
    
    @version            1.0.0 - initial release
    @version            2.0.0 - updated to class , and created MG_smallMovement
       
    @brief              This class let you perform small movement to an object

    Usage : 
    
    \code{.py}
    from MG_Tools.python.anim.GUI import MG_smallMovementGUIOld
    reload(MG_smallMovementGUIOld)
    ui = MG_smallMovementGUIOld.MG_smallMovementGUIOld()
    ui.showUi()
    
    \endcode
    '''

    def __init__(self):
        '''
        This is the constructor
        '''
        #args
       
        
        #vars        
        self.currentSel = None
        self.mainClass  = MG_smallMovement.MG_smallMovement()

        #modules
    def showUi(self):
        if cmds.window("mainWIndow", query = True , ex=True ):
            cmds.deleteUI("mainWIndow")
        
        self.window = cmds.window("mainWIndow",title="MG Small Move v2.0",wh=(250,220))
        self.mainLayout= cmds.columnLayout (adj=True)
        self.layout= cmds.rowColumnLayout (numberOfColumns=3, columnWidth=[(1, 79), (2, 79), (3, 79)])
        cmds.text(label = "")
        self.upButton  = cmds.button(label=str(chr(30)),command=self.smallUp)
        cmds.text(label = "")
        self.leftButton = cmds.button(label=str(chr(17)),command=self.smallLeft)
        self.valueField = cmds.floatField("valueField")
        self.rightButton = cmds.button(label=">",command=self.smallRight)
        cmds.text(label = "")
        self.downButton =cmds.button(label=str(chr(31)),command = self.smallDown)
        cmds.text(label ="")
        cmds.setParent(self.mainLayout)
        self.defaultAttr = cmds.checkBoxGrp("defaultAttr",numberOfCheckBoxes=3,l1="translate",l2="rotate",l3="scale",adjustableColumn3=True,on1=self.translateOn,on2=self.rotateOn,on3=self.scaleOn,v1=1)
        self.thirdAxe = cmds.checkBox("thirdAxe",label="Third axe")
        self.customAttr = cmds.checkBox("customAttr",label="Use custom Attr")
        self.loadButton=cmds.button(label="Load Custom Attr",command=self.loadCustom)
        self.scrollField = cmds.textScrollList("scrollField",h=80)
        self.scrolClumn = cmds.columnLayout (adj=True)
        cmds.showWindow(self.window)

            
    def smallUp(self,*args):
        attribute=""
        if cmds.checkBoxGrp("defaultAttr",q=True,v1=True)==1:
            attribute="t"
        if cmds.checkBoxGrp("defaultAttr",q=True,v2=True)==1:
            attribute="r"
        if cmds.checkBoxGrp("defaultAttr",q=True,v3=True)==1:
            attribute="s"
            
    
        value = cmds.floatField("valueField",q=True ,value=True)
        value = float(value)
        
        thirdAxeOnIff = cmds.checkBox ("thirdAxe",q=True,value=True)
        
        if thirdAxeOnIff == 0 :
            self.mainClass.setIncrement( attrName = [attribute + "y"] , increment = value , add = 1 )
  
        elif thirdAxeOnIff==1 :
            self.mainClass.setIncrement( attrName = [attribute + "z"] , increment = value , add = 1 )
            
        
    def smallDown(self,*args):
        attribute=""
        if cmds.checkBoxGrp("defaultAttr",q=True,v1=True)==1:
            attribute="t"
        if cmds.checkBoxGrp("defaultAttr",q=True,v2=True)==1:
            attribute="r"
        if cmds.checkBoxGrp("defaultAttr",q=True,v3=True)==1:
            attribute="s"
          
        value = cmds.floatField("valueField",q=True ,value=True)
        value = float(value)
        thirdAxeOnIff = cmds.checkBox ("thirdAxe",q=True,value=True)
        if thirdAxeOnIff == 0 :
            self.mainClass.setIncrement( attrName = [attribute + "y"] , increment = value , add = 0 )

        elif thirdAxeOnIff==1 :
            self.mainClass.setIncrement( attrName = [attribute + "z"] , increment = value , add = 0 )
        
    def smallLeft(self,*args):
        attribute=""
        if cmds.checkBoxGrp("defaultAttr",q=True,v1=True)==1:
            attribute="t"
        if cmds.checkBoxGrp("defaultAttr",q=True,v2=True)==1:
            attribute="r"
        if cmds.checkBoxGrp("defaultAttr",q=True,v3=True)==1:
            attribute="s"
            
    
        value = cmds.floatField("valueField",q=True ,value=True)
        value = float(value)
        
        customAttrOnOff = cmds.checkBox ("customAttr",q=True,value=True)
        if customAttrOnOff==0 :
            self.mainClass.setIncrement( attrName = [attribute + "x"] , increment = value , add = 0 )
            
        elif  customAttrOnOff==1:
            
            selected = cmds.textScrollList("scrollField",query=True, si=True)[0]
            if selected:
                self.mainClass.setIncrement( attrName = [selected] , increment = value , add = 0 )
    
    
    def smallRight(self,*args):
        attribute=""
        if cmds.checkBoxGrp("defaultAttr",q=True,v1=True)==1:
            attribute="t"
        if cmds.checkBoxGrp("defaultAttr",q=True,v2=True)==1:
            attribute="r"
        if cmds.checkBoxGrp("defaultAttr",q=True,v3=True)==1:
            attribute="s"
            
        val = cmds.floatField("valueField",q=True ,value=True)
        val = float(val)
        customAttrOnOff = cmds.checkBox ("customAttr",q=True,value=True)
        if customAttrOnOff==0 :
            self.mainClass.setIncrement( attrName = [attribute + "x"] , increment = val , add = 1 )
        elif  customAttrOnOff==1:
            selected = cmds.textScrollList("scrollField",query=True, si=True)[0]
            if selected:
                self.mainClass.setIncrement( attrName = [selected] , increment = val , add = 1 )
    
    def loadCustom(self,*args):
        selection  = cmds.ls(sl=True)
        if selection : 
            selection = selection[0]
        AttrList = cmds.listAttr(selection,ud=True,k=True)
        count=0
        if AttrList:
            for attr in AttrList:
                if attr == "tag":
                    AttrList.pop(count)
                    break
                count+=1
        cmds.textScrollList("scrollField",edit=True,ra=True)
        if AttrList : 
            for attr in AttrList:
                cmds.textScrollList("scrollField",edit=True,a=attr)
    
        
    def translateOn(self,*args):
        cmds.checkBoxGrp("defaultAttr",e=True,v2=0,v3=0)
    def rotateOn(self,*args):
        cmds.checkBoxGrp("defaultAttr",e=True,v1=0,v3=0)
    def scaleOn(self,*args):
        cmds.checkBoxGrp("defaultAttr",e=True,v2=0,v1=0)

def show():
    smallMove=MG_smallMovementGUIOld()
    smallMove.showUi()