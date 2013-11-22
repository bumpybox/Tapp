import os
import sys
import shutil

import config

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def installMaya():
    
    #establishing paths
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

def installNuke():
    
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

if __name__ == '__main__':
    
    #maya install
    if query_yes_no('Install Tapp for Maya?'):
        
        installMaya()
    
    if query_yes_no('Install Tapp for Nuke?'):
        
        installNuke()