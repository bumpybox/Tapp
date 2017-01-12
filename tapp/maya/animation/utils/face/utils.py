import maya.cmds as cmds

from bbt_maya import generic

def getFaceCam():
    
    meta=generic.Meta()
    
    sel=cmds.ls(selection=True)
    
    faceCam=''
    
    if len(sel)<1:
        # warning if nothing is selected
        cmds.warning('Nothing is selected! Select a control first.')
        
        return
    else:
        node=sel[0]
        
        # warning if selection is not a control type
        if meta.getData(node)['type']!='control':
            cmds.warning('Selection is not a control! Select a control first.')
            
            return
        else:
            # getting root node
            root=meta.upStream(node,'root')
            
            # getting face camera from all cameras
            cameras=meta.downStream(root, 'camera',allNodes=True)
            for camera in cameras:
                if meta.getData(camera)['component']=='face':
                    faceCam=cmds.listConnections('%s.message' % camera,type='transform')[0]
    
    return faceCam