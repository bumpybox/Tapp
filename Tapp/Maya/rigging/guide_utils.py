import maya.cmds as cmds

import Tapp.Maya.rigging.guide as mrg
reload(mrg)
import Tapp.Maya.rigging.utils as mru

def replaceParent():
    
    sel=cmds.ls(selection=True)
    
    parent=sel[-1]
    children=sel[0:-1]
    
    for child in children:
    
        cmds.deleteAttr( child, at='parent' )
        
        plong=cmds.ls(parent,long=True)[0]
        
        cmds.addAttr(child,ln='parent',at='enum',k=True,
                     enumName=':'.join(['None',plong]),defaultValue=1)

def selectionConstruct(extensionRemove=''):
    
    sel=cmds.ls(selection=True)
    
    for node in sel:
        
        p=mrg.constructor()
        
        mru.Snap(node,p)
        
        cmds.rename(p,node.replace(extensionRemove,''))

replaceParent()
#selectionConstruct('_jnt')
#mrg.constructor()