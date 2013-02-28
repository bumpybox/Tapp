import sys
import os

import nuke

path=nuke.pluginPath()[0]+'/Tapp.config'

if os.path.exists(path):
    f=open(path,'r')
    path=f.readline()

    if os.path.exists(path):
        if not path in sys.path:
            sys.path.append(path)
    
    #run setup
    import Tapp
else:
    if nuke.ask('Tapp repository is not found!\nWould you like to locate it?'):
        TappDir=nuke.getFilename('Locate Tapp repository.')
    
        #confirm that this is the Tapp directory
        if TappDir.split('/')[-2]!='Tapp':
            nuke.message('Selected directory is not the \'Tapp\' directory. Please try again')
        else:
            f=open(path,'w')
            f.write(TappDir)
            f.close()
    
            #run setup
            sys.path.append(TappDir)
            
            import Tapp