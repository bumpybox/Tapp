import sys
import os

import maya.cmds as cmds

def Change():
    ''' Changes the repository path from user input. '''
    
    #prompt user for repository path
    repoPath=cmds.fileDialog2(dialogStyle=1,fileMode=3)
    
    #changes repository path
    if repoPath!=None:
        __change__(repoPath[0])

def __change__(repoPath):
    ''' Changes the repository path from argument input. 
        repoPath = directory to repository, with '\\' separator.
    '''
    
    check=False
    #checking all subdirectories
    for name in os.listdir(repoPath):
        
        #confirm that this is the Tapp directory
        if name=='Tapp':
            check=True
    
    if check:
        #create the text file that contains the tapp directory path
        path=cmds.internalVar(upd=True)+'Tapp.config'
        
        f=open(path,'w')
        f.write(repoPath)
        f.close()

        #run setup
        sys.path.append(repoPath)
        
        cmds.evalDeferred('import Tapp')
        cmds.evalDeferred('reload(Tapp)')
        
    else:
        cmds.warning('Selected directory is not the \'Tapp\' directory. Please try again')

def Read():
    cmds.confirmDialog(title='Tapp Repository Path',message=__read__(),button='OK')

def __read__():
    path=cmds.internalVar(upd=True)+'Tapp.config'
    
    f=open(path,'r')
    
    return f.read()