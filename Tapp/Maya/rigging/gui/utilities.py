import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum

def skeletonParent():
    pass

for node in cmds.ls(type='network'):
    
    data=mum.GetData(node)
    if data['type']=='joint':
        print node