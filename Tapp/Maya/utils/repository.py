import sys

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
    
    #confirm that this is the tapp directory
    if repoPath.rpartition('\\')[-1]!='Tapp':
        cmds.warning('Selected directory is not the \'Tapp\' directory. Please try again')
    else:
        #create the text file that contains the tapp directory path
        path=cmds.internalVar(upd=True)+'Tapp.config'
        
        f=open(path,'w')
        f.write(repoPath)
        f.close()

        #run setup
        sys.path.append(repoPath)
        
        cmds.evalDeferred('import Tapp')

def Read():
    cmds.confirmDialog(title='Tapp Repository Path',message=__read__(),button='OK')

def __read__():
    path=cmds.internalVar(upd=True)+'Tapp.config'
    
    f=open(path,'r')
    
    return f.read()