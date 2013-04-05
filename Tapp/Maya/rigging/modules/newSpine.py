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
    
    #systems
    fksystem=True
    iksystem=True
    
    #initial setup---
    
    #creating asset
    asset=cmds.container(n=prefix+'rig',type='dagContainer')
    
    #setup asset
    attrs=['tx','ty','tz','ry','rz','rx','sx','sy','sz','v']
    mru.ChannelboxClean(asset, attrs)
    
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
    
    #create jnts---
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
    
    #create fk---
    
    if fksystem:
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
            
            #channelbox clean
            attrs=['v']
            mru.ChannelboxClean(cnt, attrs,lock=False)
        
        #parent to plug
        cmds.parent(fkgrps[0],plug)
    
    #create ik---
    
    if iksystem:
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
        
        cmds.parent(ikrootgrp,plug)
        cmds.parent(ikrootcnt,ikrootgrp)
        cmds.parent(ikstartcnt,ikstartgrp)
        cmds.parent(ikendcnt,ikendgrp)
        
        cmds.xform(ikrootgrp,translation=startTrans,rotation=startRot)
        mru.ClosestOrient(jnts[0],ikrootgrp)
        cmds.xform(ikstartgrp,translation=startTrans,rotation=startRot)
        mru.ClosestOrient(jnts[0],ikstartgrp)
        cmds.xform(ikendgrp,translation=endTrans,rotation=endRot)
        mru.ClosestOrient(jnts[-1],ikendgrp)
        
        cmds.parent(ikstartgrp,ikrootcnt)
        cmds.parent(ikendgrp,ikrootcnt)
        
        cmds.parent(ikstart,ikstartcnt)
        cmds.parent(ikend,ikendcnt)
        
        attrs=['v']
        mru.ChannelboxClean(ikrootcnt, attrs,lock=False)
        mru.ChannelboxClean(ikstartcnt, attrs,lock=False)
        mru.ChannelboxClean(ikendcnt, attrs,lock=False)
        
        #create pathSpine
        pathSpine=mpps.MG_pathSpine(curve, jointAmount-1)
        
        #setup pathSpine
        for key in pathSpine:
            cmds.container(asset,e=True,addNode=pathSpine[key])
        
        cmds.delete(pathSpine['root'])
        del(pathSpine['root'])
        
        ikpathspine=cmds.rename(pathSpine['MG_pathSpine'],prefix+'ik_pathSpine')
        
        cmds.rename(pathSpine['vector'],prefix+'ik_vector')
        
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
        
        iktwistendgrp=cmds.group(empty=True,n=prefix+'ik_twistend_grp')
        cmds.container(asset,e=True,addNode=iktwistendgrp)
        mru.Snap(iktwistend, iktwistendgrp)
        cmds.parent(iktwistendgrp,ikrootcnt)
        cmds.parent(iktwistend,iktwistendgrp)
        
        iktwiststartgrp=cmds.group(empty=True,n=prefix+'ik_twiststart_grp')
        cmds.container(asset,e=True,addNode=iktwiststartgrp)
        mru.Snap(iktwiststart, iktwiststartgrp)
        cmds.parent(iktwiststartgrp,ikrootcnt)
        cmds.parent(iktwiststart,iktwiststartgrp)
        
        cmds.parent(ikupvectors,ikrootcnt)
        cmds.parentConstraint(ikstartcnt,iktwiststart,maintainOffset=True)
        cmds.parentConstraint(ikendcnt,iktwistend,maintainOffset=True)
        
        cmds.setAttr(ikpathspine+'.keepTwistVolume',0)
        cmds.connectAttr(plug+'.sx',ikpathspine+'.globalScale')
        
        #individual controls
        ikcnts=[]
        ikgrps=[]
        
        for count in xrange(1,jointAmount+1):
            
            #create fk controls
            [grp,cnt]=mru.Square(prefix+'ik'+str(count)+'_cnt',
                           group=True)
            
            cmds.container(asset,e=True,addNode=[grp,cnt])
            
            #setup fk controls
            cmds.parent(cnt,grp)
            
            mru.Snap(jnts[count-1], grp)
            
            if len(ikcnts)<jointAmount-1:
                
                cmds.parent(grp,iklocators[count-1])
            
            data={'system':'ik','index':count}
            mNode=mum.SetData(('meta_'+cnt),'control',
                               'joint',module,data)
            mum.SetTransform(cnt, mNode)
            
            ikcnts.append(cnt)
            ikgrps.append(grp)
            
            attrs=['v']
            mru.ChannelboxClean(cnt, attrs,lock=False)
        
        cmds.parent(ikgrps[-1],ikendcnt)
    
    #blending system---
    
    if iksystem and fksystem:
        
        #create extra control
        extracnt=mru.Pin(prefix+'extra_cnt')
        
        mNode=mum.SetData(('meta_'+extracnt),'control',
                           'extra',module,None)
        mum.SetTransform(extracnt, mNode)
        
        cmds.container(asset,e=True,addNode=extracnt)
        
        #setup extra control
        mru.Snap(jnts[-1],extracnt)
        
        cmds.parent(extracnt,jnts[-1])
        
        cmds.setAttr(extracnt+'.ry',-90)
        
        cmds.addAttr(extracnt,ln='squashStretch',at='float',
                     keyable=True,min=0,max=1)
        cmds.addAttr(extracnt,ln='FKIK',at='float',
                     keyable=True,min=0,max=1)
        
        cmds.connectAttr(extracnt+'.squashStretch',ikpathspine+'.stretchMult')
        cmds.connectAttr(extracnt+'.squashStretch',ikpathspine+'.stretch')
        cmds.connectAttr(extracnt+'.squashStretch',ikpathspine+'.squashMult')
        
        fkikREV=cmds.shadingNode('reverse',asUtility=True,
                                 n=prefix+'fkikREV')
        cmds.connectAttr(extracnt+'.FKIK',fkikREV+'.inputX')
        
        attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
        mru.ChannelboxClean(extracnt, attrs)
        
        #setup jnts
        for count in xrange(1,jointAmount+1):
            
            parentCon=cmds.parentConstraint(ikcnts[count-1],fkcnts[count-1],jnts[count-1])[0]
            scaleCon=cmds.scaleConstraint(ikcnts[count-1],fkcnts[count-1],jnts[count-1])[0]
            
            cmds.connectAttr(fkikREV+'.outputX',parentCon+'.'+fkcnts[count-1]+'W1')
            cmds.connectAttr(extracnt+'.FKIK',parentCon+'.'+ikcnts[count-1]+'W0')
            cmds.connectAttr(fkikREV+'.outputX',scaleCon+'.'+fkcnts[count-1]+'W1')
            cmds.connectAttr(extracnt+'.FKIK',scaleCon+'.'+ikcnts[count-1]+'W0')
        
        #setup controls
        for cnt in fkcnts:
            cmds.connectAttr(fkikREV+'.outputX',cnt+'.v')
        
        for cnt in ikcnts:
            cmds.connectAttr(extracnt+'.FKIK',cnt+'.v')
        
        cmds.connectAttr(extracnt+'.FKIK',ikendcnt+'.v')
        cmds.connectAttr(extracnt+'.FKIK',ikstartcnt+'.v')
        cmds.connectAttr(extracnt+'.FKIK',ikrootcnt+'.v')
    
    #hip control---
    if hipsAttach and spineType=='spine':
        #create hip jnt
        cmds.select(cl=True)
        jnt=cmds.joint(position=(0,0,0),name=prefix+'hip_jnt')
        
        cmds.container(asset,e=True,addNode=jnt)
        
        #setup jnt
        
        meta=mum.SetData('meta_'+jnt, 'joint', 'hip', module, None)
        mum.SetTransform(jnt, meta)
        
        mru.Snap(ikrootcnt,jnt)
        cmds.makeIdentity(jnt,apply=True,t=1,r=1,s=1,n=0)
        
        cmds.move(-spineLength/3,0,0,jnt,r=True,os=True)
        
        #create socket
        socket=cmds.spaceLocator(n=prefix+'socket')[0]
        
        data={'index':jointAmount+2}
        meta=mum.SetData('meta_'+socket,'socket',None,module,data)
        mum.SetTransform(socket,meta)
    
        cmds.container(asset,e=True,addNode=socket)
        
        #setup socket
        mru.Snap(jnt,socket)
        
        cmds.parent(socket,jnt)
        
        #create hip control
        [grp,cnt]=mru.Circle(prefix+'hip_cnt', group=True)
        
        meta=mum.SetData('meta_'+cnt,'control','hip',module, None)
        mum.SetTransform(cnt, meta)
        
        cmds.container(asset,e=True,addNode=[grp,cnt])
        
        #setup hip control
        cmds.parent(cnt,grp)
        mru.Snap(jnt,grp)
        mru.Snap(jnts[0], grp)
        
        cmds.parent(jnt,cnt)
        cmds.parent(grp,plug)
        
        cmds.move(-spineLength/3,0,0,cnt+'.cv[0:7]',
                  r=True,os=True)
        
        #setup hip extra control
        cmds.addAttr(extracnt,ln='hipFollow',at='float',
                     keyable=True,min=0,max=1)
        
        hipREV=cmds.shadingNode('reverse',asUtility=True,
                                 n=prefix+'hipREV')
        
        cmds.connectAttr(extracnt+'.hipFollow',
                         hipREV+'.inputX')
        
        parentGRP=cmds.group(empty=True,
                             n=prefix+'hipParent_grp')
        pointGRP=cmds.group(empty=True,
                            n=prefix+'hipPoint_grp')
        
        cmds.container(asset,e=True,addNode=[parentGRP,
                                             pointGRP])
        
        mru.Snap(cnt,parentGRP)
        mru.Snap(cnt,pointGRP)
        
        cmds.parent(parentGRP,jnts[0])
        cmds.parent(pointGRP,plug)
        cmds.pointConstraint(jnts[0],pointGRP,
                             maintainOffset=True)
        
        pCon=cmds.parentConstraint(parentGRP,pointGRP,grp)[0]
        
        cmds.connectAttr(extracnt+'.hipFollow',
                         pCon+'.'+parentGRP+'W0')
        cmds.connectAttr(hipREV+'.outputX',
                         pCon+'.'+pointGRP+'W1')
        
        #clean channel box
        attrs=['v']
        mru.ChannelboxClean(cnt, attrs)
        
#templateModule='spine:meta_spine'
#Rig(templateModule)