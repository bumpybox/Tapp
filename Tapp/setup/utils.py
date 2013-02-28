import os
import shutil

import config

def InstallMaya():
    
    #establising paths
    configPath=os.path.dirname(config.__file__)
    appPath=os.environ['USERPROFILE']+'/Documents/maya/scripts'
    
    #copying tapp script
    shutil.copy2(configPath+'/tapp_maya.py', appPath)
    
    #query userSetup file
    cmd='import tapp_maya'
    
    if not os.path.exists(appPath+'/userSetup.py'):
        
        f=open(appPath+'/userSetup.py','w')
        f.write(cmd)
        f.close()
    else:
        
        f=open(appPath+'/userSetup.py','r')
        fdata=f.read()
        
        fdict=fdata.split('\n')
        
        #check if cmd is not already in userSetup
        if not cmd in fdict:
            
            #writing cmd to userSetup
            data=cmd+'\n'+fdata
            
            f=open(appPath+'/userSetup.py','w')
            f.write(data)
            f.close()

def InstallNuke():
    
    #establising paths
    configPath=os.path.dirname(config.__file__)
    appPath=os.environ['USERPROFILE']+'/.nuke'
    
    #copying tapp script
    shutil.copy2(configPath+'/tapp_nuke.py', appPath)
    
    #query userSetup file
    cmd='import tapp_nuke'
    
    if not os.path.exists(appPath+'/menu.py'):
        
        f=open(appPath+'/menu.py','w')
        f.write(cmd)
        f.close()
    else:
        
        f=open(appPath+'/menu.py','r')
        fdata=f.read()
        
        fdict=fdata.split('\n')
        
        #check if cmd is not already in userSetup
        if not cmd in fdict:
            
            #writing cmd to userSetup
            data=cmd+'\n'+fdata
            
            f=open(appPath+'/menu.py','w')
            f.write(data)
            f.close()