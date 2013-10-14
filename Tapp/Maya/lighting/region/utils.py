'''
- arnold
    - subtracts 1 pixel from min values
    - adds 2 pixels to max values
'''

import maya.cmds as cmds

class region():
    
    def __init__(self,frame,minX,maxX,minY,maxY):
        
        self.frame=frame
        self.minX=minX
        self.maxX=maxX
        self.minY=minY
        self.maxY=maxY

def getRegionDraw():
    
    minX=cmds.getAttr('defaultRenderGlobals.left')
    maxX=cmds.getAttr('defaultRenderGlobals.rght')
    minY=cmds.getAttr('defaultRenderGlobals.bot')
    maxY=cmds.getAttr('defaultRenderGlobals.top')
    
    return {'minX':minX,'maxX':maxX,'minY':minY,'maxY':maxY}

def getRegionNode():
    
    result=[]
    
    for layer in cmds.ls(type='renderLayer'):
        
        #search for existing region nodes
        node=cmds.listConnections('%s.message' % layer,type='network')
        
        #create node if none existing
        if not node:
            node=cmds.shadingNode('network',n='regionNode_'+layer,asUtility=True)
        else:
            node=node[0]
        
        #adding attributes
        attrs=['minX','maxX','minY','maxY']
        for attr in attrs:
            if not cmds.objExists(node+'.'+attr):
                cmds.addAttr(node,ln=attr,defaultValue=0,attributeType='long')
        
        #connecting to renderlayer
        if not cmds.objExists(node+'.'+'renderlayer'):
            cmds.addAttr(node,ln='renderlayer',attributeType='message')
            
            cmds.connectAttr(layer+'.message',node+'.renderlayer')
        
        #return node
        result.append(node)
    
    return result
    
print getRegionNode()