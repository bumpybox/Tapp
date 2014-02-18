from maya import  cmds , OpenMaya , mel
from MG_Tools.python.utils import jsonUtils
import os

class MG_smallMovement (object):
    '''
    
    @author             Marco Giordano
     
    @date               04.23.2013
    
    @version            1.0.0
       
    @brief              This class let you perform small movement to an object

    Usage : 
    
    \code{.py}
    
    \endcode
    '''

    def __init__(self):
        '''
        This is the constructor
        '''
        #args
       
        
        #vars        
        self.currentSel = None
        #modules
        self.jsonUtils = jsonUtils.jsonUtils()

    def checkSelected(self):
        '''
        This procedure check if something is selected otherwise shoots out an error
        @return: list 
        '''
        
        sel = cmds.ls(sl = 1)
        if not sel :
            OpenMaya.MGlobal.displayError("Please select something")
            return
        
        self.currentSel = sel
    
    
    
    def setIncrement(self , attrName = None , increment = None , add = 1 ):
        '''
        This procedure sets the increment on the object
        '''
        self.checkSelected()
        if increment == 0 :
            return
        if not self.currentSel :
            return
        
        if not attrName :
            attrName = self.getSelectedChannels()
            if not attrName :
                return
            
        if not increment :
            increment    = self.getIncrementFromFile()
            if not increment :
                return
        
        for s in self.currentSel:
            for a in attrName:
                if cmds.objExists(s + '.' + a ) == 1 :
                    value = cmds.getAttr(s + '.' + a)
                    if add == 1 :

                        value = value + increment
                    else :
                        value = value - increment
                        
                    cmds.setAttr(s + '.' + a , value)
                    
    def getSelectedChannels (self):
    
        channelBox = mel.eval('$temp=$gChannelBoxName')
        chList = cmds.channelBox (channelBox, q=True, sma = True)
        
        if chList:
            return chList
        else:
            OpenMaya.MGlobal.displayError("No Channels selected")
            return
        
    def getIncrementFromFile(self):
        '''
        This procedure gets the stored increment in the file
        '''
        path = mel.eval('getenv MAYA_SCRIPT_PATH ;')
        path = str(path.split(";")[0]) +'/MG_smallMovement.prefs'
        if os.path.isfile(path) == 1 :
            dictValue = self.jsonUtils.load(path)
            return dictValue["increment"]
        
        else :
            OpenMaya.MGlobal.displayError("There is not pref file stored ")
            return

        
    
    def storeIncrementToFile(self , value = None):
        
        if not value :
            result = cmds.promptDialog(
            title='',
            message='Increment value:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')
            if result == 'OK':
                value  = float(cmds.promptDialog(query=True, text=True))
            else :
                return
        toStore = {"increment" : value}
        path = mel.eval('getenv MAYA_SCRIPT_PATH ;')
        path = str(path.split(";")[0]) +'/MG_smallMovement.prefs'
        self.jsonUtils.save(toStore, path)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    