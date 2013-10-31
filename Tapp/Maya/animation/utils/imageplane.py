import os
import shutil

import maya.cmds as cmds

def localizeImagePlane():
    sel=cmds.ls(selection=True)
    
    if len(sel)==1:
        
        if cmds.nodeType(sel[0])=='imagePlane':
            
            ip=sel[0]
            
            f=cmds.getAttr(ip+'.imageName')
            
            user_profile = os.environ['USERPROFILE']
            user_desktop = user_profile + "/Desktop"
            path=os.path.join(user_desktop,os.path.basename(f))
            
            shutil.copy(f,path)
            
            cmds.setAttr(ip+'.imageName',path,type='string')
            
        else:
            cmds.warning('Selected node is not an image plane!')
    elif len(sel)==0:
        cmds.warning('Nothing is selected!')
        return
    else:
        cmds.warning('Multiple nodes selected. Please select one node only!')