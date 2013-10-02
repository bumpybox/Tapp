import os

import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru
import Tapp.Maya.utils.ZvParentMaster as muz

def Create():
    ''' Imports the template module to rig.
        returns imported nodes.
    '''
    
    path=os.path.realpath(__file__)
    
    filePath=path.replace('\\','/').split('.py')[0]+'.ma'
    
    return cmds.file(filePath,i=True,defaultNamespace=False,
                     returnNewNodes=True,renameAll=True,
                     mergeNamespacesOnClash=True,
                     namespace='foot')
    
def __createMirror__(module):
    
    return Create()

def Attach(childModule,parentModule):
    
    data=mum.GetData(parentModule)
    if data['component']=='limb':
        
        plugs=mum.DownStream(parentModule, 'plug')
        ikPlug=''
        for plug in plugs:
            
            data=mum.GetData(plug)
            if 'system' in data:
                ikPlug=mum.GetTransform(plug)
        
        cmds.select(ikPlug,r=True)
        muz.detach()
        
        #getting controls
        ikballcnt=''
        controls=mum.DownStream(childModule, 'control')
        for cnt in controls:
            
            data=mum.GetData(cnt)
            
            if data['component']=='ball':
                ikballcnt=mum.GetTransform(cnt)
        
        #getting joints
        ikfoot=''
        iks=mum.DownStream(childModule, 'ik')
        for ik in iks:
            
            data=mum.GetData(ik)
            
            if data['component']=='foot':
                ikfoot=mum.GetTransform(ik)
        
        #getting groups
        rbankParent=''
        grps=mum.DownStream(childModule, 'group')
        for grp in grps:
            
            data=mum.GetData(grp)
            
            if data['component']=='bank' and data['side']=='right':
                rbankParent=mum.GetTransform(grp)
        
        #getting plug
        plug=mum.DownStream(childModule, 'plug')[0]
        plug=mum.GetTransform(plug)
        
        #getting asset
        asset=cmds.container(q=True,fc=ikballcnt)
        
        #attaching ik plug
        cmds.select(ikPlug,ikballcnt,r=True)
        muz.attach()
        
        #create fk foot align
        fkfootalign=cmds.group(empty=True,
                               n=ikfoot+'_align')
        
        cmds.container(asset,e=True,addNode=[fkfootalign])
        
        mru.Snap(ikfoot,fkfootalign)
        
        cmds.parent(fkfootalign,ikfoot)
        
        #setup controls
        sockets=mum.DownStream(parentModule,'socket')
        
        controls=mum.DownStream(parentModule, 'control')
        for cnt in controls:
            data=mum.GetData(cnt)
            
            #setup ik control
            if 'system' in data and data['system']=='ik' \
            and data['component']=='end':
                tn=mum.GetTransform(cnt)
                
                cmds.select(rbankParent,tn,r=True)
                muz.attach()
                
                cmds.scaleConstraint(tn,rbankParent)
            
            #setup extra control
            if data['component']=='extra':
                tn=mum.GetTransform(cnt)
                
                cmds.connectAttr(tn+'.FKIK',asset+'.FKIK')
            
            #setup end fk control
            if 'system' in data and data['system']=='fk' \
            and data['component']=='end':
                data={'switch':fkfootalign}
                mum.ModifyData(cnt, data)
                
                tn=mum.GetTransform(cnt)
                
                mru.Snap(tn,fkfootalign,point=False)
        
        #attaching plug
        for socket in sockets:
            data=mum.GetData(socket)
            
            if data['index']=='3':
                tn=mum.GetTransform(socket)
                
                cmds.select(plug,tn,r=True)
                muz.attach()
                
                cmds.scaleConstraint(tn,plug)
        
        #connecting modules
        cmds.connectAttr(parentModule+'.message',childModule+'.metaParent')
    else:
        mru.Attach(childModule, parentModule)

def Detach(module):
    pass

def SetWorld(childModule,worldModule,downStream=False):
    
    #attaching child module to parent module
    mru.SetWorld(childModule, worldModule,downStream)

def Rig(module):
    ''' Rigs the provided module. '''
    
    #collect all components
    controls=mum.DownStream(module,'control')
    
    for control in controls:
        data=mum.GetData(control)
        
        if data['component']=='foot':
            foot=mum.GetTransform(control)
        if data['component']=='toe':
            toe=mum.GetTransform(control)
        if data['component']=='toetip':
            toetip=mum.GetTransform(control)
        if data['component']=='heel':
            heel=mum.GetTransform(control)
        if data['component']=='bank' and data['side']=='right':
            rbank=mum.GetTransform(control)
        if data['component']=='bank' and data['side']=='left':
            lbank=mum.GetTransform(control)
    
    #getting transform data
    footTrans=cmds.xform(foot,worldSpace=True,query=True,
                          translation=True)
    toeTrans=cmds.xform(toe,worldSpace=True,query=True,
                          translation=True)
    toetipTrans=cmds.xform(toetip,worldSpace=True,query=True,
                          translation=True)
    heelTrans=cmds.xform(heel,worldSpace=True,query=True,
                          translation=True)
    heelRot=cmds.xform(heel,worldSpace=True,query=True,
                          rotation=True)
    rbankTrans=cmds.xform(rbank,worldSpace=True,query=True,
                          translation=True)
    rbankRot=cmds.xform(rbank,worldSpace=True,query=True,
                          rotation=True)
    lbankTrans=cmds.xform(lbank,worldSpace=True,query=True,
                          translation=True)
    lbankRot=cmds.xform(lbank,worldSpace=True,query=True,
                          rotation=True)
    
    #getting module data
    data=mum.GetData(module)
    
    fk=True
    ik=True
    
    #establish side
    side='center'
    
    x=(footTrans[0]+toetipTrans[0]+heelTrans[0])/3
    
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
        data['type']=='module' and \
        data['side']==side and \
        data['index']==index:
            index+=1
    
    #delete template
    cmds.delete(cmds.container(q=True,fc=foot))
    
    #establish prefix and suffix
    prefix=side[0]+'_'+'foot'+str(index)+'_'
    suffix='_'+side[0]+'_'+'foot'+str(index)
    
    #initial setup---
    
    #creating asset
    asset=cmds.container(n=prefix+'rig',type='dagContainer')
    
    #setup asset
    attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
    mru.ChannelboxClean(asset, attrs)
    
    #create module
    data={'side':side,'index':str(index),'system':'rig','subcomponent':'foot'}
    
    module=mum.SetData(('meta'+suffix),'module','foot',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #create plug
    plug=cmds.spaceLocator(name=prefix+'plug')[0]
    
    #setup plug
    metaParent=mum.SetData('meta_'+plug,'plug',None,module,
                            None)
    
    mum.SetTransform(plug, metaParent)
    
    phgrp=cmds.group(empty=True,n=(plug+'_PH'))
    sngrp=cmds.group(empty=True,n=(plug+'_SN'))
    
    cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
    
    cmds.parent(sngrp,phgrp)
    cmds.parent(plug,sngrp)
    
    cmds.xform(phgrp,worldSpace=True,translation=footTrans)
    
    #create jnts---
    
    #create joints
    cmds.select(cl=True)
    footJNT=cmds.joint(position=(footTrans[0],footTrans[1],
                                    footTrans[2]),
                          name=prefix+'jnt01')
    cmds.select(cl=True)
    toeJNT=cmds.joint(position=(toeTrans[0],toeTrans[1],
                                    toeTrans[2]),
                          name=prefix+'jnt02')
    
    cmds.container(asset,e=True,addNode=[footJNT,toeJNT])
    
    #finding the upVector for the joints
    crs=mru.CrossProduct(footTrans,toeTrans,toetipTrans)
    
    #setup foot joint
    meta=mum.SetData('meta_'+footJNT, 'joint', None, module, None)
    mum.SetTransform(footJNT, meta)
    
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=footTrans)
    cmds.aimConstraint(toeJNT,grp,worldUpType='vector',
                       worldUpVector=crs)
    
    rot=cmds.xform(grp,query=True,rotation=True)
    cmds.rotate(rot[0],rot[1],rot[2],footJNT,
                worldSpace=True,pcp=True)
    
    cmds.makeIdentity(footJNT,apply=True,t=1,r=1,s=1,n=0)
    
    cmds.delete(grp)
    
    #setup toe joint    
    meta=mum.SetData('meta_'+toeJNT, 'joint', None, module, None)
    mum.SetTransform(toeJNT, meta)
    
    grp=cmds.group(empty=True)
    temp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=toeTrans)
    cmds.xform(temp,worldSpace=True,translation=toetipTrans)
    cmds.aimConstraint(temp,grp,worldUpType='vector',
                       worldUpVector=crs)
    
    rot=cmds.xform(grp,query=True,rotation=True)
    cmds.rotate(rot[0],rot[1],rot[2],toeJNT,worldSpace=True,
                pcp=True)
    
    cmds.delete(grp)
    cmds.delete(temp)
    
    cmds.makeIdentity(toeJNT,apply=True, t=1, r=1, s=1, n=0)
    
    #create sockets
    socket01=cmds.spaceLocator(name=prefix+'socket01')[0]
    socket02=cmds.spaceLocator(name=prefix+'socket02')[0]
    
    #setup sockets
    cmds.xform(socket01,worldSpace=True,translation=footTrans)
    cmds.xform(socket02,worldSpace=True,translation=toeTrans)
    
    cmds.container(asset,e=True,addNode=[socket01,socket02])
    
    cmds.parent(socket01,footJNT)
    cmds.parent(socket02,toeJNT)
    
    data={'index':1}
    metaParent=mum.SetData('meta_'+socket01,'socket',None,
                            module,data)
    mum.SetTransform(socket01, metaParent)
    data={'index':2}
    metaParent=mum.SetData('meta_'+socket02,'socket',None,
                            module,data)
    mum.SetTransform(socket02, metaParent)
    
    #create fk---
    if fk:
        
        #create fk chain
        fkfoot=cmds.duplicate(footJNT,st=True,po=True,
                               n=prefix+'fk_01')[0]
        fktoe=cmds.duplicate(toeJNT,st=True,po=True,
                               n=prefix+'fk_02')[0]
        
        cmds.container(asset,e=True,addNode=[fkfoot,fktoe])
        
        #setup fk chain
        cmds.parent(fktoe,fkfoot)
        
        cmds.parent(fkfoot,plug)
        
        #create controls
        fktoecnt=mru.Square(prefix+'fk_toe_cnt')
        
        #setup fktoecnt
        data={'system':'fk','index':4}
        mNode=mum.SetData(('meta_'+fktoecnt),'control','toe',
                           module,data)
        mum.SetTransform(fktoecnt, mNode)
        
        grp=cmds.group(empty=True,n=(fktoecnt+'_grp'))
        
        cmds.container(asset,e=True,addNode=grp)
        
        cmds.parent(fktoecnt,grp)
        cmds.parent(grp,plug)
        
        mru.Snap(toeJNT,grp)
        
        cmds.parent(fktoe,fktoecnt)
        cmds.parent(grp,fkfoot)
        
        #channelbox clean
        attrs=['tx','ty','tz','sx','sy','sz']
        mru.ChannelboxClean(fktoecnt, attrs)
        
        attrs=['v']
        mru.ChannelboxClean(fktoecnt, attrs,lock=False)
        
        #publish controls
        cmds.containerPublish(asset,publishNode=(fktoecnt,''))
        cmds.containerPublish(asset,bindNode=(fktoecnt,fktoecnt))
    
    #create ik---
    if ik:
    
        #create ik chain
        ikfoot=cmds.duplicate(footJNT,st=True,po=True,
                               n=prefix+'ik_01')[0]
        iktoe=cmds.duplicate(toeJNT,st=True,po=True,
                               n=prefix+'ik_02')[0]
        
        cmds.container(asset,e=True,addNode=[ikfoot,iktoe])
        
        #setup ik chain
        mNode=mum.SetData('meta_'+ikfoot, 'ik', 'foot', module, None)
        mum.SetTransform(ikfoot, mNode)
        
        cmds.parent(iktoe,ikfoot)
        
        #create controls
        ikballcnt=mru.Circle(prefix+'ik_ball_cnt')
        iktoecnt=mru.Circle(prefix+'ik_toe_cnt')
        iktoetipcnt=mru.Sphere(prefix+'ik_toetip_cnt')
        ikheelcnt=mru.Sphere(prefix+'ik_heel_cnt')
        ikfootcnt=mru.Sphere(prefix+'ik_foot_cnt')
        
        cmds.container(asset,e=True,addNode=[ikballcnt,iktoecnt,
                                             iktoetipcnt,ikheelcnt,
                                             ikfootcnt])
        
        #create right bank
        ikrbankgrp=cmds.group(empty=True,n=prefix+'ik_r_bank_grp')
        ikrbankgrpGRP=cmds.group(empty=True,n=ikrbankgrp+'_grp')
        
        cmds.container(asset,e=True,addNode=[ikrbankgrp,ikrbankgrpGRP])
        
        #setup right bank
        cmds.parent(ikrbankgrp,ikrbankgrpGRP)
        
        rbankParent=cmds.group(empty=True,n=ikrbankgrp+'_parent')
        
        cmds.container(asset,e=True,addNode=rbankParent)
        
        mru.Snap(plug,rbankParent)
        
        cmds.parent(ikrbankgrpGRP,rbankParent)
        
        data={'side':'right'}
        mNode=mum.SetData('meta_'+rbankParent, 'group', 'bank', module, data)
        mum.SetTransform(rbankParent, mNode)
        
        cmds.xform(ikrbankgrpGRP,ws=True,translation=rbankTrans)
        cmds.xform(ikrbankgrpGRP,ws=True,rotation=rbankRot)
        
        cmds.rotate(-90,0,0,ikrbankgrpGRP,r=True,os=True)
        cmds.rotate(0,0,-90,ikrbankgrpGRP,r=True,os=True)
        
        phgrp=cmds.group(empty=True,n=(rbankParent+'_PH'))
        sngrp=cmds.group(empty=True,n=(rbankParent+'_SN'))
        
        cmds.container(asset,e=True,addNode=[phgrp,sngrp])
        
        mru.Snap(rbankParent,phgrp)
        mru.Snap(rbankParent,sngrp)
        
        cmds.parent(sngrp,phgrp)
        cmds.parent(rbankParent,sngrp)
        
        #create left bank
        iklbankgrp=cmds.group(empty=True,n=prefix+'ik_l_bank_grp')
        
        cmds.container(asset,e=True,addNode=[iklbankgrp])
        
        #setup left bank
        grp=cmds.group(empty=True,n=iklbankgrp+'_grp')
        
        cmds.container(asset,e=True,addNode=grp)
        
        cmds.parent(iklbankgrp,grp)
        
        cmds.xform(grp,ws=True,translation=lbankTrans)
        cmds.xform(grp,ws=True,rotation=lbankRot)
        
        cmds.rotate(-90,0,0,grp,r=True,os=True)
        cmds.rotate(0,0,-90,grp,r=True,os=True)
        
        cmds.parent(grp,ikrbankgrp)
        
        #setup ikheelcnt
        data={'system':'ik','index':8}
        mNode=mum.SetData(('meta_'+ikheelcnt),'control','heel',
                           module,data)
        mum.SetTransform(ikheelcnt, mNode)
        
        ikheelgrp=cmds.group(empty=True,n=(ikheelcnt+'_grp'))
        grp=cmds.group(empty=True,n=(ikheelgrp+'_grp'))
        
        cmds.container(asset,e=True,addNode=[ikheelgrp,grp])
        
        cmds.parent(ikheelcnt,ikheelgrp)
        cmds.parent(ikheelgrp,grp)
        
        cmds.xform(grp,ws=True,rotation=heelRot)
        cmds.xform(grp,ws=True,translation=heelTrans)
        
        cmds.rotate(-90,0,0,grp,r=True,os=True)
        cmds.rotate(0,0,-90,grp,r=True,os=True)
        
        cmds.parent(grp,iklbankgrp)
        
        #setup iktoetipcnt
        data={'system':'ik','index':7}
        mNode=mum.SetData(('meta_'+iktoetipcnt),'control','toetip',
                           module,data)
        mum.SetTransform(iktoetipcnt, mNode)
        
        iktoetipgrp=cmds.group(empty=True,n=(iktoetipcnt+'_grp'))
        grp=cmds.group(empty=True,n=(iktoetipgrp+'_grp'))
        
        cmds.container(asset,e=True,addNode=[iktoetipgrp,grp])
        
        cmds.parent(iktoetipcnt,iktoetipgrp)
        cmds.parent(iktoetipgrp,grp)
        
        cmds.xform(grp,ws=True,rotation=heelRot)
        cmds.xform(grp,ws=True,translation=toetipTrans)
        
        cmds.parent(grp,ikheelcnt)
        
        cmds.rotate(-90,0,0,grp,r=True,os=True)
        cmds.rotate(0,0,-90,grp,r=True,os=True)
        
        #setup ikballcnt
        data={'system':'ik','index':6}
        mNode=mum.SetData(('meta_'+ikballcnt),'control','ball',
                           module,data)
        mum.SetTransform(ikballcnt, mNode)
        
        cmds.scale(1.5,1.5,1.5,ikballcnt)
        cmds.makeIdentity(ikballcnt,apply=True, t=1, r=1, s=1, n=0)
        
        ikballgrp=cmds.group(empty=True,n=(ikballcnt+'_grp'))
        grp=cmds.group(empty=True,n=ikballgrp+'_grp')
        
        cmds.container(asset,e=True,addNode=[ikballgrp,grp])
        
        cmds.parent(ikballcnt,ikballgrp)
        cmds.parent(ikballgrp,grp)
        
        mru.Snap(toeJNT,grp)
        
        cmds.parent(grp,iktoetipcnt)
        
        #setup iktoecnt
        data={'system':'ik','index':5}
        mNode=mum.SetData(('meta_'+iktoecnt),'control','toe',
                           module,data)
        mum.SetTransform(iktoecnt, mNode)
        
        iktoegrp=cmds.group(empty=True,n=(iktoecnt+'_grp'))
        grp=cmds.group(empty=True,n=(iktoegrp+'_grp'))
        
        cmds.container(asset,e=True,addNode=[iktoegrp,grp])
        
        cmds.parent(iktoecnt,iktoegrp)
        cmds.parent(iktoegrp,grp)
        
        mru.Snap(toeJNT,grp)
        
        cmds.parent(grp,iktoetipcnt)
        
        #setup ikfootcnt
        data={'system':'ik','index':4}
        mNode=mum.SetData(('meta_'+ikfootcnt),'control','foot',
                           module,data)
        mum.SetTransform(ikfootcnt, mNode)
        
        ikfootgrp=cmds.group(empty=True,n=(ikfootcnt+'_grp'))
        
        cmds.container(asset,e=True,addNode=ikfootgrp)
        
        cmds.parent(ikfootcnt,ikfootgrp)
        
        cmds.parent(ikfootgrp,rbankParent)
        
        cmds.xform(ikfootgrp,ws=True,rotation=heelRot)
        cmds.xform(ikfootgrp,ws=True,translation=heelTrans)
        cmds.move(0,0,-2,ikfootgrp,r=True,os=True)
        
        cmds.rotate(-90,0,0,ikfootgrp,r=True,os=True)
        cmds.rotate(0,0,-90,ikfootgrp,r=True,os=True)
        
        #setup foot controls
        cmds.transformLimits(ikfootcnt,ry=[-90,90],ery=[1,1],
                             rx=[-90,90],erx=[1,1])
        
        cmds.transformLimits(ikrbankgrp,rx=[-90,0],erx=[1,1])
        cmds.transformLimits(iklbankgrp,rx=[0,90],erx=[1,1])
        
        cmds.transformLimits(ikheelgrp,ry=[0,0],ery=[0,1])
        cmds.transformLimits(ikballgrp,ry=[0,0],ery=[1,0])
        
        cmds.connectAttr(ikfootcnt+'.rx',ikrbankgrp+'.rx')
        cmds.connectAttr(ikfootcnt+'.rx',iklbankgrp+'.rx')
        cmds.connectAttr(ikfootcnt+'.ry',ikheelgrp+'.ry')
        
        unit01=cmds.shadingNode('unitConversion',asUtility=True)
        unit02=cmds.shadingNode('unitConversion',asUtility=True)
        unit03=cmds.shadingNode('unitConversion',asUtility=True)
        foot01REMAP=cmds.shadingNode('remapValue',asUtility=True,
                                     n=prefix+'foot01_remap')
        foot02REMAP=cmds.shadingNode('remapValue',asUtility=True,
                                     n=prefix+'foot02_remap')
        footPMS=cmds.shadingNode('plusMinusAverage',asUtility=True,
                                     n=prefix+'foot_pms')
        
        cmds.addAttr(ikfootcnt,ln='footLift',at='float',min=0,max=90,
                     k=True)
        
        cmds.setAttr(ikfootcnt+'.footLift',33)
        cmds.setAttr(unit01+'.conversionFactor',57.29578)
        cmds.setAttr(unit02+'.conversionFactor',0.0174533)
        cmds.setAttr(unit03+'.conversionFactor',0.0174533)
        cmds.setAttr(foot01REMAP+'.inputMax',90)
        cmds.setAttr(foot01REMAP+'.outputMin',0)
        cmds.setAttr(foot01REMAP+'.outputMax',90)
        cmds.setAttr(foot02REMAP+'.inputMax',90)
        cmds.setAttr(foot02REMAP+'.outputMin',0)
        cmds.setAttr(foot02REMAP+'.outputMax',-90)
        cmds.setAttr(footPMS+'.operation',1)
        
        cmds.connectAttr(ikfootcnt+'.ry',unit01+'.input')
        cmds.connectAttr(ikfootcnt+'.footLift',
                         foot01REMAP+'.inputMin')
        cmds.connectAttr(ikfootcnt+'.footLift',
                         foot02REMAP+'.inputMin')
        cmds.connectAttr(unit01+'.output',
                         foot01REMAP+'.inputValue')
        cmds.connectAttr(unit01+'.output',
                         foot02REMAP+'.inputValue')
        cmds.connectAttr(unit01+'.output',footPMS+'.input1D[0]')
        cmds.connectAttr(foot01REMAP+'.outColorR',unit02+'.input')
        cmds.connectAttr(unit02+'.output',iktoetipgrp+'.ry')
        cmds.connectAttr(foot02REMAP+'.outColorR',
                         footPMS+'.input1D[1]')
        cmds.connectAttr(footPMS+'.output1D',unit03+'.input')
        cmds.connectAttr(unit03+'.output',ikballgrp+'.ry')
        
        cmds.parent(ikfoot,ikballcnt)
        cmds.parent(iktoe,iktoecnt)
        
        cmds.pointConstraint(plug,ikfoot)
        
        #clean channel box
        cnts=[ikballcnt,iktoecnt,iktoetipcnt,ikheelcnt,ikfootcnt]
        
        attrs=['tx','ty','tz','sx','sy','sz']
        for cnt in cnts:
            mru.ChannelboxClean(cnt, attrs)
        
        attrs=['v']
        for cnt in cnts:
            mru.ChannelboxClean(cnt, attrs,lock=False)
        
        #publishing controllers
        for cnt in cnts:
            
            cmds.containerPublish(asset,publishNode=(cnt,''))
            cmds.containerPublish(asset,bindNode=(cnt,cnt))
    
    #blending---
    if fk and ik:
    
        #create zero groups
        ikfootcntzero=cmds.group(empty=True,n=ikfootcnt+'_zero')
        zerocnt=cmds.createNode('transform',ss=True,
                                n=prefix+'zero_cnt')
        
        cmds.container(asset,e=True,addNode=[zerocnt,ikfootcntzero])
        
        #setup zero groups
        cmds.parent(ikfootcntzero,ikfootgrp)
        
        mru.Snap(ikfootcnt,ikfootcntzero)
        
        mru.Snap(ikheelcnt, zerocnt)
        
        cmds.parent(zerocnt,plug)
    
        #blending setup
        cmds.addAttr(asset,ln='FKIK',at='float',min=0,max=1,
                     k=True)
        
        fkikREV=cmds.shadingNode('reverse',asUtility=True,
                                 n=prefix+'fkikREV')
        
        cmds.connectAttr(asset+'.FKIK',fkikREV+'.inputX')
        
        con=cmds.parentConstraint(ikfoot,fkfoot,footJNT)[0]
        cmds.connectAttr(fkikREV+'.outputX',
                         con+'.'+fkfoot+'W1')
        cmds.connectAttr(asset+'.FKIK',
                         con+'.'+ikfoot+'W0')
        
        con=cmds.scaleConstraint(ikfoot,fkfoot,footJNT)[0]
        cmds.connectAttr(fkikREV+'.outputX',
                         con+'.'+fkfoot+'W1')
        cmds.connectAttr(asset+'.FKIK',
                         con+'.'+ikfoot+'W0')
        
        con=cmds.parentConstraint(iktoe,fktoe,toeJNT)[0]
        cmds.connectAttr(fkikREV+'.outputX',
                         con+'.'+fktoe+'W1')
        cmds.connectAttr(asset+'.FKIK',
                         con+'.'+iktoe+'W0')
        
        con=cmds.scaleConstraint(iktoe,fktoe,toeJNT)[0]
        cmds.connectAttr(fkikREV+'.outputX',
                         con+'.'+fktoe+'W1')
        cmds.connectAttr(asset+'.FKIK',
                         con+'.'+iktoe+'W0')
        
        cmds.connectAttr(fkikREV+'.outputX',fktoecnt+'.v')
        cmds.connectAttr(asset+'.FKIK',ikballcnt+'.v')
        cmds.connectAttr(asset+'.FKIK',iktoecnt+'.v')
        cmds.connectAttr(asset+'.FKIK',iktoetipcnt+'.v')
        cmds.connectAttr(asset+'.FKIK',ikheelcnt+'.v')
        cmds.connectAttr(asset+'.FKIK',ikfootcnt+'.v')
        
        #setup switching
        data={'switch':zerocnt}
        mum.ModifyData(ikheelcnt, data)
        
        data={'switch':zerocnt}
        mum.ModifyData(iktoetipcnt, data)
        
        data={'switch':zerocnt}
        mum.ModifyData(ikballcnt, data)
        
        data={'switch':fktoe}
        mum.ModifyData(iktoecnt, data)
        
        data={'switch':ikfootcntzero}
        mum.ModifyData(ikfootcnt, data)
        
        data={'switch':iktoe}
        mum.ModifyData(fktoecnt, data)

#Attach('meta_c_foot1','meta_c_arm1')
#templateModule='foot:meta_foot'
#Rig(templateModule)