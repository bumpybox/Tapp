import sys

import maya.cmds as cmds

class Repository():
    
    def Change(self):
        ''' Changes the repository path from user input. '''
        
        #prompt user for repository path
        repoPath=cmds.fileDialog2(dialogStyle=1,fileMode=3)
        
        #changes repository path
        if repoPath!=None:
            self.__change__(repoPath[0])
    
    def __change__(self,repoPath):
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