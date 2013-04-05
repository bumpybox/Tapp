import os

import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru
import MG_Tools.python.MG_pathSpine as mpps

def Create():
    ''' Imports the template module to rig.
        returns imported nodes.
    '''
    
    path=os.path.realpath(__file__)
    
    filePath=path.replace('\\','/').split('.py')[0]+'.ma'
    
    return cmds.file(filePath,i=True,defaultNamespace=False,
                     returnNewNodes=True,renameAll=True,
                     mergeNamespacesOnClash=True,
                     namespace='spine')

def __createMirror__(module):
    
    return Create()

def Attach(childModule,parentModule):
    
    #attaching child module to parent module
    mru.Attach(childModule, parentModule)

def Detach(module):
    pass

def SetWorld(childModule,worldModule,downStream=False):
    
    #attaching child module to parent module
    mru.SetWorld(childModule, worldModule,downStream)

def Rig(module):
    ''' Rigs the provided spine module. '''
    
    #collect all components
    controls=mum.DownStream(module,'control')
    
    for control in controls:
        if mum.GetData(control)['component']=='start':
            start=mum.GetTransform(control)
        if mum.GetData(control)['component']=='line':
            line=mum.GetTransform(control)
        if mum.GetData(control)['component']=='end':
            end=mum.GetTransform(control)
    
    #getting module data
    data=mum.GetData(module)
    
    jointAmount=int(data['joints'])
    hipsAttach=data['hips']
    spineType=data['spineType']
    
    #getting transform data
    startTrans=cmds.xform(start,worldSpace=True,query=True,
                          translation=True)
    startRot=cmds.xform(start,worldSpace=True,query=True,
                      rotation=True)
    endTrans=cmds.xform(end,worldSpace=True,query=True,
                        translation=True)
    endRot=cmds.xform(end,worldSpace=True,query=True,
                      rotation=True)
    
    spineLength=mru.Distance(start, end)
    
    #establish side
    side='center'
    
    x=(startTrans[0]+endTrans[0])/2
    
    if x>0.1:
        side='left'
    if x<-0.1:
        side='right'
    
    #establish index
    data=mum.GetData(module)
    
    index=int(data['index'])
    
    for node in cmds.ls(type='network'):
        data=mum.GetData(node)
        if 'index' in data.keys() and \
        'side' in data.keys() and \
        'component' in data.keys() and \
        data['type']=='module' and \
        data['side']==side and \
        data['index']==index:
            index+=1
    
    #delete template
    cmds.delete(cmds.container(q=True,fc=start))
    
    #establish prefix and suffix
    prefix=side[0]+'_'+spineType+str(index)+'_'
    suffix='_'+side[0]+'_'+spineType+str(index)
    
    #creating asset
    asset=cmds.container(n=prefix+'rig',type='dagContainer')
    
    #create module
    data={'side':side,'index':str(index),'system':'rig','subcomponent':spineType}
    
    module=mum.SetData(('meta'+suffix),'module','spine',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #create plug
    plug=cmds.spaceLocator(name=prefix+'plug')[0]
    
    phgrp=cmds.group(empty=True,n=(plug+'_PH'))
    sngrp=cmds.group(empty=True,n=(plug+'_SN'))
    
    cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
    
    #setup plug
    cmds.parent(sngrp,phgrp)
    cmds.parent(plug,sngrp)
    
    cmds.xform(phgrp,worldSpace=True,translation=startTrans)
    
    metaParent=mum.SetData('meta_'+plug,'plug',None,module,
                            None)
    
    mum.SetTransform(plug, metaParent)
    
    #create jnts------------------------------------------------------
    jnts=[]
    sockets=[]
    
    for count in xrange(1,jointAmount+1):
        
        #create joint
        jnt=cmds.joint(position=((spineLength/(jointAmount-1))*count,0,0),
                       name=prefix+'jnt'+str(count))
        
        cmds.container(asset,e=True,addNode=jnt)
        
        #setup joint
        if len(jnts)>0:
            cmds.parent(jnt,jnts[-1])
        
        jnts.append(jnt)
        
        #create socket
        socket=cmds.spaceLocator(name=prefix+'socket'+
                                 str(count))[0]
        
        cmds.container(asset,e=True,addNode=socket)
        
        #setup socket
        mru.Snap(jnt,socket)
        cmds.parent(socket,jnt)
        
        data={'index':count}
        metaParent=mum.SetData('meta_'+socket,'socket',None,
                                module,data)
        mum.SetTransform(socket, metaParent)
        
        sockets.append(socket)
    
    #transforming chain
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=endTrans)
    
    cmds.xform(jnts[0],worldSpace=True,translation=startTrans)
    cmds.delete(cmds.aimConstraint(grp,jnts[0],
                                  worldUpVector=(1,0,0)))
    
    cmds.delete(grp)
    
    #parent to plug
    cmds.parent(jnts[0],plug)
    
    '''
    #create fk chain------------------------------------------------------------
    fkcnts=[]
    fkgrps=[]
    
    for count in xrange(1,jointAmount+1):
        
        #create fk controls
        [grp,cnt]=mru.Square(prefix+'fk'+str(count)+'_cnt',
                       group=True)
        
        cmds.container(asset,e=True,addNode=[grp,cnt])
        
        #setup fk controls
        cmds.parent(cnt,grp)
        
        mru.Snap(jnts[count-1], grp)
        
        if len(fkcnts)>0:
            cmds.parent(grp,fkcnts[-1])
        
        data={'system':'fk','index':count}
        mNode=mum.SetData(('meta_'+cnt),'control',
                           'joint',module,data)
        mum.SetTransform(cnt, mNode)
        
        fkcnts.append(cnt)
        fkgrps.append(grp)
    
    #parent to plug
    cmds.parent(fkgrps[0],plug)
    '''
    
    #create ik chain-----------------------------------------------------------
    
    #create curve
    curve=cmds.curve(d=1,p=[startTrans,endTrans],n=prefix+'ik_curve')
    
    cmds.container(asset,e=True,addNode=curve)
    
    #setup curve
    cmds.rebuildCurve(curve,rpo=1,rt=0,end=1,kr=0,kcp=0,kep=1,kt=0,s=1,d=2,tol=0.01)
    
    cmds.select(cl=True)
    ikstart=cmds.joint(position=startTrans,n=prefix+'ik_start')
    cmds.select(cl=True)
    ikend=cmds.joint(position=endTrans,n=prefix+'ik_end')
    
    cmds.container(asset,e=True,addNode=[ikstart,ikend])
    
    skin=cmds.skinCluster(ikstart,ikend,curve,tsb=True)
    
    cmds.skinPercent(skin[0],curve+'.cv[0]',tv=[(ikstart,1.0)])
    cmds.skinPercent(skin[0],curve+'.cv[1]',tv=[(ikstart,1.0)])
    cmds.skinPercent(skin[0],curve+'.cv[2]',tv=[(ikend,1.0)])
    cmds.skinPercent(skin[0],curve+'.cv[3]',tv=[(ikend,1.0)])
    
    #create controls
    [ikrootgrp,ikrootcnt]=mru.Circle(prefix+'ik_root_cnt', group=True)
    [ikstartgrp,ikstartcnt]=mru.Sphere(prefix+'ik_start_cnt', group=True)
    [ikendgrp,ikendcnt]=mru.Sphere(prefix+'ik_end_cnt', group=True)
    
    #setup controls
    cmds.container(asset,e=True,addNode=[ikrootcnt,ikrootgrp])
    cmds.container(asset,e=True,addNode=[ikstartcnt,ikstartgrp])
    cmds.container(asset,e=True,addNode=[ikendcnt,ikendgrp])
    
    cmds.parent(ikrootcnt,ikrootgrp)
    cmds.parent(ikstartcnt,ikstartgrp)
    cmds.parent(ikendcnt,ikendgrp)
    
    cmds.xform(ikrootgrp,translation=startTrans,rotation=startRot)
    mru.ClosestOrient(jnts[0],ikrootgrp)
    cmds.xform(ikstartgrp,translation=startTrans,rotation=startRot)
    mru.ClosestOrient(jnts[0],ikstartgrp)
    cmds.xform(ikendgrp,translation=endTrans,rotation=endTrans)
    mru.ClosestOrient(jnts[-1],ikendgrp)
    
    cmds.parent(ikstartgrp,ikrootcnt)
    cmds.parent(ikendgrp,ikrootcnt)
    
    cmds.parent(ikstart,ikstartcnt)
    cmds.parent(ikend,ikendcnt)
    
    #create pathSpine
    pathSpine=mpps.MG_pathSpine(curve, jointAmount-1)
    
    #setup pathSpine
    for key in pathSpine:
        cmds.container(asset,e=True,addNode=pathSpine[key])
    
    cmds.delete(pathSpine['root'])
    del(pathSpine['root'])
    
    iktwistend=cmds.rename(pathSpine['twist_end'],prefix+'ik_twistend')
    iktwiststart=cmds.rename(pathSpine['twist_start'],prefix+'ik_twiststart')
    
    ikupvectors=[]
    for item in pathSpine['up_vector']:
        
        item=cmds.rename(item,prefix+'ik_upvector1')
        
        ikupvectors.append(item)
    
    iklocators=[]
    for item in pathSpine['locators']:
        
        item=cmds.rename(item,prefix+'ik_loc1')
        
        iklocators.append(item)
    
    cmds.parent(ikupvectors,ikrootcnt)
    cmds.parent(iktwiststart,ikrootcnt)
    cmds.parent(iktwistend,ikrootcnt)
    cmds.parentConstraint(ikstartcnt,iktwiststart,maintainOffset=True)
    cmds.parentConstraint(ikendcnt,iktwistend,maintainOffset=True)
    
    cmds.setAttr(pathSpine['MG_pathSpine']+'.keepTwistVolume',0)
    
    #NEED TO CREATE INDIVIDUAL CONTROLS
        
templateModule='spine:meta_spine'
Rig(templateModule)