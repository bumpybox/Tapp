'''
- need to account for render layers
    - have a regionNode per renderlayer
- arnold
    - subtracts 1 pixel from min values
    - adds 2 pixels to max values
'''

import pymel.core as pc

class region():
    
    def __init__(self,frame,minX,maxX,minY,maxY):
        
        self.frame=frame
        self.minX=minX
        self.maxX=maxX
        self.minY=minY
        self.maxY=maxY

def getRegionDraw():
    
    drg=pc.PyNode('defaultRenderGlobals')
    
    minX=drg.left.get()
    maxX=drg.rght.get()
    minY=drg.bot.get()
    maxY=drg.top.get()
    
    return {'minX':minX,'maxX':maxX,'minY':minY,'maxY':maxY}

def createRegionNode():
    
    result=None
    
    for node in pc.ls(type='network'):
        if node.name()=='regionNode':
            result=node
    
    if not result:
        result=pc.createNode('network',n='regionNode')
    
    attrs=['minX','maxX','minY','maxY']
    
    
    try:
        pc.addAttr(result,ln='minX',defaultValue=0)
        pc.addAttr(result,ln='maxX',defaultValue=0)
        pc.addAttr(result,ln='minY',defaultValue=0)
        pc.addAttr(result,ln='maxY',defaultValue=0)
    except:
        pass
    
createRegionNode()