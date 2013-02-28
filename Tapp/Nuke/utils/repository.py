import sys
import os

import nuke
 
def Change():
    ''' Changes the repository path from user input. '''
    
    #prompt user for repository path
    repoPath=nuke.getFilename('Locate Tapp repository.')
    
    #changes repository path
    if repoPath!=None:
        __change__(repoPath)

def __change__(repoPath):
    ''' Changes the repository path from argument input. 
        repoPath = directory to repository.
    '''
    
    path=nuke.pluginPath()[0]+'/Tapp.config'
    
    if os.path.exists(path):
        f=open(path,'w')
        f.write(repoPath)
        f.close()
    
        if os.path.exists(repoPath):
            if not path in sys.path:
                sys.path.append(repoPath)
        
        #run setup
        import Tapp