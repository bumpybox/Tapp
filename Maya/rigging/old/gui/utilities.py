import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru

def SkeletonParent():
    ''' Parents selection to closest joint in rig. ''' 
    
    cmds.undoInfo(openChunk=True)
    
    for obj in cmds.ls(selection=True):
        
        if cmds.nodeType(obj)=='joint':
        
            nodes={}
            for node in cmds.ls(type='network'):
                
                data=mum.GetData(node)
                if data['type']=='joint':
                    
                    tn=mum.GetTransform(node)
                    nodes[tn]=mru.Distance(tn, obj)
            
            closestJnt=min(nodes, key=nodes.get)
            
            cmds.parentConstraint(closestJnt,obj,mo=True)
            #cmds.scaleConstraint(closestJnt,obj)
            
            #scaling linking
            cmds.connectAttr(closestJnt+'.sx',obj+'.sx')
            cmds.connectAttr(closestJnt+'.sy',obj+'.sy')
            cmds.connectAttr(closestJnt+'.sz',obj+'.sz')
            
            #cmds.setAttr(obj+'.inheritsTransform',0)
            
            #cmds.setAttr(obj+'.segmentScaleCompensate',0)
    
    cmds.undoInfo(closeChunk=True)

def ___sphereDist__():
    #create nodes
    sph=cmds.polySphere(ch=True,name='spherePreview_geo')
    
    edgeGroup=cmds.group(empty=True,name='spherePreview_group')
    
    dist=cmds.createNode('distanceBetween')
    
    #setup group
    cmds.move(0,0,1,edgeGroup)
    
    #setup sphere
    cmds.connectAttr('%s.worldMatrix' % sph[0],'%s.inMatrix1' % dist)
    
    cmds.connectAttr('%s.worldMatrix' % edgeGroup,'%s.inMatrix2' % dist)
    
    cmds.connectAttr('%s.distance' % dist,'%s.radius' % sph[1])
    
    #create metaData
    meta=cmds.shadingNode('network',asUtility=True,name='meta_spherePreview')
    cmds.addAttr(meta,longName='type',dataType='string')
    cmds.setAttr('%s.type' % meta,'spherePreview',type='string')
    cmds.addAttr(meta,longName='createJoints',dataType='string')
    cmds.addAttr(meta,longName='sphere',attributeType='message')
    cmds.addAttr(meta,longName='group',attributeType='message')
    
    cmds.addAttr(sph[0],longName='metaParent',attributeType='message')
    cmds.addAttr(edgeGroup,longName='metaParent',attributeType='message')
    cmds.addAttr(dist,longName='metaParent',attributeType='message')
    
    cmds.connectAttr('%s.message' % meta,'%s.metaParent' % sph[0])
    cmds.connectAttr('%s.message' % meta,'%s.metaParent' % edgeGroup)
    cmds.connectAttr('%s.message' % meta,'%s.metaParent' % dist)
    cmds.connectAttr('%s.message' % sph[0],'%s.sphere' % meta)
    cmds.connectAttr('%s.message' % edgeGroup,'%s.group' % meta)
    
    #return
    return (sph[0],edgeGroup,meta)

def SpherePreview():
    selCount=len(cmds.ls(sl=True))
    
    #zero selected
    if selCount==0:
        #create locator
        loc=cmds.spaceLocator(name='spherePreview_loc')[0]
        
        #create sphere
        nodes=___sphereDist__()
        
        #setup sphere
        cmds.pointConstraint(loc,nodes[1])
        
        #setup loc        
        cmds.move(0,0,1,loc)
        
        #attach metaData
        cmds.addAttr(loc,longName='metaParent',attributeType='message')
        
        cmds.connectAttr('%s.message' % nodes[2],'%s.metaParent' % loc)
        
        cmds.setAttr('%s.createJoints' % nodes[2],'true',type='string')
    
    #one item selected
    if selCount==1:
        #getting selection
        sel=cmds.ls(sl=True)[0]
        
        #create locator
        loc=cmds.spaceLocator(name='spherePreview_loc')[0]
        
        #create sphere
        nodes=___sphereDist__()
        
        #setup sphere
        cmds.pointConstraint(loc,nodes[1])
        
        cmds.delete(cmds.pointConstraint(sel,nodes[0]))
        
        #setup loc
        cmds.delete(cmds.pointConstraint(sel,loc))
        
        cmds.move(0,0,1,loc,relative=True)

        #attach metaData
        cmds.addAttr(loc,longName='metaParent',attributeType='message')
        
        cmds.connectAttr('%s.message' % nodes[2],'%s.metaParent' % loc)
        
        cmds.setAttr('%s.createJoints' % nodes[2],'true',type='string')

    #one item selected
    if selCount==2:
        #getting selection
        sel1=cmds.ls(sl=True)[0]
        
        sel2=cmds.ls(sl=True)[1]
        
        #create sphere
        nodes=___sphereDist__()
        
        #setup sphere
        cmds.pointConstraint(sel1,nodes[0])
        
        cmds.pointConstraint(sel2,nodes[1])
        
        #setup metaData
        cmds.setAttr('%s.createJoints' % nodes[2],'false',type='string')

def SpherePreviewDelete():
    for node in (cmds.ls(type='network')):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='spherePreview':
            if (cmds.getAttr('%s.createJoints' % node))=='true':
                #create joints
                cmds.select(cl=True)
                jnt1=cmds.joint()
                
                cmds.select(cl=True)
                jnt2=cmds.joint()
                
                #setup joints
                sph=cmds.listConnections('%s.sphere' % node,type='transform')
                cmds.delete(cmds.pointConstraint(sph,jnt1))
                
                grp=cmds.listConnections('%s.group' % node,type='transform')
                cmds.delete(cmds.pointConstraint(grp,jnt2))
                
                cmds.delete(cmds.aimConstraint(grp,jnt1))
                cmds.makeIdentity(jnt1,apply=True)
                
                cmds.delete(cmds.orientConstraint(jnt1,jnt2))
                cmds.makeIdentity(jnt2,apply=True)
                
                cmds.parent(jnt2,jnt1)
            
            for child in cmds.listConnections('%s.message' % node,type='transform'):
                cmds.delete(child)