import maya.cmds as cmds

def replaceParent():
    
    sel=cmds.ls(selection=True)
    
    parent=sel[-1]
    children=sel[0:-1]
    
    for child in children:
    
        cmds.deleteAttr( child, at='parent' )
        
        plong=cmds.ls(parent,long=True)[0]
        
        cmds.addAttr(child,ln='parent',at='enum',k=True,
                     enumName=':'.join(['None',plong]),defaultValue=1)

replaceParent()