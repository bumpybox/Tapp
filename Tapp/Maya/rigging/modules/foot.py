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
    
    filePath=path.replace('\\','/').split('.')[0]+'.ma'
    
    return cmds.file(filePath,i=True,defaultNamespace=False,
                     returnNewNodes=True,renameAll=True)

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
    
    attachToLeg=data['attachToLeg']
    
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
    
    #creating asset
    asset=cmds.container(n=prefix+'rig')
    
    #create module
    data={'side':side,'index':str(index),'system':'rig'}
    
    module=mum.SetData(('meta'+suffix),'module','foot',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #create joints
    footJNT=cmds.joint(position=(footTrans[0],footTrans[1],
                                    footTrans[2]),
                          name=prefix+'jnt01')
    toeJNT=cmds.joint(position=(toeTrans[0],toeTrans[1],
                                    toeTrans[2]),
                          name=prefix+'jnt02')
    
    cmds.container(asset,e=True,addNode=[footJNT,toeJNT])
    
    #setup joints
    meta=mum.SetData('meta_'+footJNT, 'joint', None, module, None)
    mum.SetTransform(footJNT, meta)
    
    meta=mum.SetData('meta_'+toeJNT, 'joint', None, module, None)
    mum.SetTransform(toeJNT, meta)
    
    #create plug
    plug=cmds.spaceLocator(name=prefix+'plug')[0]
    
    phgrp=cmds.group(plug,n=(plug+'_PH'))
    sngrp=cmds.group(plug,n=(plug+'_SN'))
    
    cmds.xform(phgrp,worldSpace=True,translation=footTrans)
    
    metaParent=mum.SetData('meta_'+plug,'plug',None,module,
                            None)
    
    mum.SetTransform(plug, metaParent)
    
    cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
    
    #create sockets
    socket01=cmds.spaceLocator(name=prefix+'socket01')[0]
    socket02=cmds.spaceLocator(name=prefix+'socket02')[0]
    
    #setup sockets
    cmds.xform(socket01,worldSpace=True,translation=footTrans)
    cmds.xform(socket02,worldSpace=True,translation=toeTrans)
    
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
    
    cmds.container(asset,e=True,addNode=[socket01,socket02])
    
    #finding the upVector for the joints
    crs=mru.CrossProduct(footTrans,toeTrans,toetipTrans)
    
    #setup foot joint
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=footTrans)
    cmds.aimConstraint(toeJNT,grp,worldUpType='vector',
                       worldUpVector=crs)
    
    rot=cmds.xform(grp,query=True,rotation=True)
    cmds.rotate(rot[0],rot[1],rot[2],footJNT,
                worldSpace=True,pcp=True)
    
    cmds.makeIdentity(footJNT,apply=True,t=1,r=1,s=1,n=0)
    
    cmds.delete(grp)
    
    cmds.parent(footJNT,plug)
    
    #setup toe joint
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
    
    #create ik chain
    footIK=cmds.duplicate(footJNT,st=True,po=True,
                           n=prefix+'ik01')[0]
    toeIK=cmds.duplicate(toeJNT,st=True,po=True,
                           n=prefix+'ik02')[0]
    
    cmds.container(asset,e=True,addNode=[footIK,toeIK])
    
    #setup ik chain
    cmds.parent(toeIK,footIK)
    
    cmds.connectAttr('%s.scale' % footIK,
                     '%s.inverseScale' % toeIK,force=True)
    
    #create fk chain
    footFK=cmds.duplicate(footJNT,st=True,po=True,
                           n=prefix+'fk01')[0]
    toeFK=cmds.duplicate(toeJNT,st=True,po=True,
                           n=prefix+'fk02')[0]
    
    cmds.container(asset,e=True,addNode=[footFK,toeFK])
    
    #setup fk chain
    cmds.parent(toeFK,footFK)
    
    cmds.connectAttr('%s.scale' % footFK,
                     '%s.inverseScale' % toeFK,force=True)
    
    #create controls
    zeroCNT=cmds.createNode('transform',ss=True,
                            n=prefix+'zero_cnt')
    
    ballCNT=mru.Circle(prefix+'ball_cnt')
    toeIkCNT=mru.Circle(prefix+'toeIk_cnt')
    toetipCNT=mru.Sphere(prefix+'toetip_cnt')
    heelCNT=mru.Sphere(prefix+'heel_cnt')
    footCNT=mru.Sphere(prefix+'foot_cnt')
    toeFkCNT=mru.Square(prefix+'toeFk_cnt')
    
    cmds.container(asset,e=True,addNode=[ballCNT,toeIkCNT,
                                         toetipCNT,heelCNT,
                                         footCNT,toeFkCNT,
                                         zeroCNT])
    
    #create right bank
    rbankGRP=cmds.group(empty=True,n=prefix+'r_bank_grp')
    rbankgrpGRP=cmds.group(rbankGRP,n=rbankGRP+'_grp')
    
    cmds.container(asset,e=True,addNode=[rbankGRP,rbankgrpGRP])
    
    #setup right bank
    rbankParent=cmds.group(empty=True,n=rbankGRP+'_parent')
    mru.Snap(plug,rbankParent)
    
    cmds.parent(rbankgrpGRP,rbankParent)
    
    phgrp=cmds.group(rbankParent,n=(rbankParent+'_PH'))
    sngrp=cmds.group(rbankParent,n=(rbankParent+'_SN'))
    
    cmds.xform(rbankgrpGRP,ws=True,translation=rbankTrans)
    cmds.xform(rbankgrpGRP,ws=True,rotation=rbankRot)
    
    cmds.rotate(-90,0,0,rbankgrpGRP,r=True,os=True)
    cmds.rotate(0,0,-90,rbankgrpGRP,r=True,os=True)
    
    cmds.container(asset,e=True,addNode=[rbankParent,phgrp,
                                         sngrp])
    
    #create left bank
    lbankGRP=cmds.group(empty=True,n=prefix+'l_bank_grp')
    
    cmds.container(asset,e=True,addNode=[lbankGRP])
    
    #setup left bank
    grp=cmds.group(lbankGRP,n=lbankGRP+'_grp')
    
    cmds.xform(grp,ws=True,translation=lbankTrans)
    cmds.xform(grp,ws=True,rotation=lbankRot)
    
    cmds.rotate(-90,0,0,grp,r=True,os=True)
    cmds.rotate(0,0,-90,grp,r=True,os=True)
    
    cmds.parent(grp,rbankGRP)
    
    cmds.container(asset,e=True,addNode=[grp])
    
    #setup heelCNT
    data={'system':'ik','switch':zeroCNT,'index':8}
    mNode=mum.SetData(('meta_'+heelCNT),'control','heel',
                       module,data)
    mum.SetTransform(heelCNT, mNode)
    
    heelGRP=cmds.group(heelCNT,n=(heelCNT+'_grp'))
    grp=cmds.group(heelGRP,n=(heelGRP+'_grp'))
    
    cmds.xform(grp,ws=True,rotation=heelRot)
    cmds.xform(grp,ws=True,translation=heelTrans)
    
    cmds.rotate(-90,0,0,grp,r=True,os=True)
    cmds.rotate(0,0,-90,grp,r=True,os=True)
    
    cmds.parent(grp,lbankGRP)
    
    cmds.container(asset,e=True,addNode=[heelGRP,grp])
    
    #setup zeroCNT
    mru.Snap(heelCNT, zeroCNT)
    
    cmds.parent(zeroCNT,plug)
    
    #setup toetipCNT
    data={'system':'ik','switch':zeroCNT,'index':7}
    mNode=mum.SetData(('meta_'+toetipCNT),'control','toetip',
                       module,data)
    mum.SetTransform(toetipCNT, mNode)
    
    toetipGRP=cmds.group(toetipCNT,n=(toetipCNT+'_grp'))
    grp=cmds.group(toetipGRP,n=(toetipGRP+'_grp'))
    
    cmds.xform(grp,ws=True,rotation=heelRot)
    cmds.xform(grp,ws=True,translation=toetipTrans)
    
    cmds.parent(grp,heelCNT)
    
    cmds.rotate(-90,0,0,grp,r=True,os=True)
    cmds.rotate(0,0,-90,grp,r=True,os=True)
    
    cmds.container(asset,e=True,addNode=[toetipGRP,grp])
    
    #setup ballCNT
    data={'system':'ik','switch':zeroCNT,'index':6}
    mNode=mum.SetData(('meta_'+ballCNT),'control','ball',
                       module,data)
    mum.SetTransform(ballCNT, mNode)
    
    cmds.scale(1.5,1.5,1.5,ballCNT)
    cmds.makeIdentity(ballCNT,apply=True, t=1, r=1, s=1, n=0)
    
    ballGRP=cmds.group(ballCNT,n=(ballCNT+'_grp'))
    grp=cmds.group(ballGRP,n=ballGRP+'_grp')
    
    mru.Snap(toeJNT,grp)
    
    cmds.parent(grp,toetipCNT)
    
    cmds.container(asset,e=True,addNode=[ballGRP,grp])
    
    #setup toeIkCNT
    data={'system':'ik','switch':toeFK,'index':5}
    mNode=mum.SetData(('meta_'+toeIkCNT),'control','toe',
                       module,data)
    mum.SetTransform(toeIkCNT, mNode)
    
    toeIkGRP=cmds.group(toeIkCNT,n=(toeIkCNT+'_grp'))
    grp=cmds.group(toeIkGRP,n=(toeIkGRP+'_grp'))
    
    mru.Snap(toeJNT,grp)
    
    cmds.parent(grp,toetipCNT)
    
    cmds.container(asset,e=True,addNode=[toeIkGRP,grp])
    
    #setup footCNT
    footCNTzero=cmds.group(empty=True,n=footCNT+'_zero')
    
    mru.Snap(footCNT,footCNTzero)
    
    data={'system':'ik','switch':footCNTzero,'index':4}
    mNode=mum.SetData(('meta_'+footCNT),'control','foot',
                       module,data)
    mum.SetTransform(footCNT, mNode)
    
    grp=cmds.group(footCNT,footCNTzero,n=(footCNT+'_grp'))
    cmds.parent(grp,rbankParent)
    
    cmds.xform(grp,ws=True,rotation=heelRot)
    cmds.xform(grp,ws=True,translation=heelTrans)
    cmds.move(0,0,-2,grp,r=True,os=True)
    
    cmds.rotate(-90,0,0,grp,r=True,os=True)
    cmds.rotate(0,0,-90,grp,r=True,os=True)
    
    cmds.container(asset,e=True,addNode=[grp,footCNTzero])
    
    #setup toeFkCNT
    data={'system':'fk','switch':toeIK,'index':4}
    mNode=mum.SetData(('meta_'+toeFkCNT),'control','toe',
                       module,data)
    mum.SetTransform(toeFkCNT, mNode)
    
    grp=cmds.group(toeFkCNT,n=(toeFkCNT+'_grp'))
    cmds.parent(grp,plug)
    
    mru.Snap(toeJNT,grp)
    
    cmds.parent(toeFK,toeFkCNT)
    
    cmds.container(asset,e=True,addNode=[grp])
    
    #setup foot controls
    cmds.transformLimits(footCNT,ry=[-90,90],ery=[1,1],
                         rx=[-90,90],erx=[1,1])
    
    cmds.transformLimits(rbankGRP,rx=[-90,0],erx=[1,1])
    cmds.transformLimits(lbankGRP,rx=[0,90],erx=[1,1])
    
    cmds.transformLimits(heelGRP,ry=[0,0],ery=[0,1])
    cmds.transformLimits(ballGRP,ry=[0,0],ery=[1,0])
    
    cmds.connectAttr(footCNT+'.rx',rbankGRP+'.rx')
    cmds.connectAttr(footCNT+'.rx',lbankGRP+'.rx')
    cmds.connectAttr(footCNT+'.ry',heelGRP+'.ry')
    
    unit01=cmds.shadingNode('unitConversion',asUtility=True)
    unit02=cmds.shadingNode('unitConversion',asUtility=True)
    unit03=cmds.shadingNode('unitConversion',asUtility=True)
    foot01REMAP=cmds.shadingNode('remapValue',asUtility=True,
                                 n=prefix+'foot01_remap')
    foot02REMAP=cmds.shadingNode('remapValue',asUtility=True,
                                 n=prefix+'foot02_remap')
    footPMS=cmds.shadingNode('plusMinusAverage',asUtility=True,
                                 n=prefix+'foot_pms')
    
    cmds.addAttr(footCNT,ln='footLift',at='float',min=0,max=90,
                 k=True)
    
    cmds.setAttr(footCNT+'.footLift',33)
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
    
    cmds.connectAttr(footCNT+'.ry',unit01+'.input')
    cmds.connectAttr(footCNT+'.footLift',
                     foot01REMAP+'.inputMin')
    cmds.connectAttr(footCNT+'.footLift',
                     foot02REMAP+'.inputMin')
    cmds.connectAttr(unit01+'.output',
                     foot01REMAP+'.inputValue')
    cmds.connectAttr(unit01+'.output',
                     foot02REMAP+'.inputValue')
    cmds.connectAttr(unit01+'.output',footPMS+'.input1D[0]')
    cmds.connectAttr(foot01REMAP+'.outColorR',unit02+'.input')
    cmds.connectAttr(unit02+'.output',toetipGRP+'.ry')
    cmds.connectAttr(foot02REMAP+'.outColorR',
                     footPMS+'.input1D[1]')
    cmds.connectAttr(footPMS+'.output1D',unit03+'.input')
    cmds.connectAttr(unit03+'.output',ballGRP+'.ry')
    
    cmds.parent(footIK,ballCNT)
    cmds.parent(toeIK,toeIkCNT)
    
    #blending setup
    cmds.addAttr(asset,ln='FKIK',at='float',min=0,max=1,
                 k=True)
    
    fkikREV=cmds.shadingNode('reverse',asUtility=True,
                             n=prefix+'fkikREV')
    
    cmds.connectAttr(asset+'.FKIK',fkikREV+'.inputX')
    
    orientCon=cmds.orientConstraint(footIK,footFK,footJNT)[0]
    cmds.connectAttr(fkikREV+'.outputX',
                     orientCon+'.'+footFK+'W1')
    cmds.connectAttr(asset+'.FKIK',
                     orientCon+'.'+footIK+'W0')
    
    orientCon=cmds.orientConstraint(toeIK,toeFK,toeJNT)[0]
    cmds.connectAttr(fkikREV+'.outputX',
                     orientCon+'.'+toeFK+'W1')
    cmds.connectAttr(asset+'.FKIK',
                     orientCon+'.'+toeIK+'W0')
    
    cmds.connectAttr(fkikREV+'.outputX',toeFkCNT+'.v')
    cmds.connectAttr(asset+'.FKIK',ballCNT+'.v')
    cmds.connectAttr(asset+'.FKIK',toeIkCNT+'.v')
    cmds.connectAttr(asset+'.FKIK',toetipCNT+'.v')
    cmds.connectAttr(asset+'.FKIK',heelCNT+'.v')
    cmds.connectAttr(asset+'.FKIK',footCNT+'.v')
    
    #attach to leg
    if attachToLeg==True:
        #search for plugs in scene and add distance to plugs
        plugs={}
        
        for node in cmds.ls(type='network'):
            data=mum.GetData(node)
            if data['type']=='module' and \
            data['component']=='limb':
                nodes=mum.DownStream(node,'plug')
                for n in nodes:
                    data=mum.GetData(n)
                    if 'system' in data:
                        tn=mum.GetTransform(n)
                        plugs[tn]=mru.Distance(tn, plug)
        
        #attaching ik plug
        ikPlug=min(plugs, key=plugs.get)
        
        cmds.select(ikPlug,r=True)
        muz.detach()
        
        cmds.select(ikPlug,ballCNT,r=True)
        muz.attach()
        
        #create fk foot align
        footFKalign=cmds.group(empty=True,
                               n=footIK+'_align')
        
        cmds.container(asset,e=True,addNode=[footFKalign])
        
        mru.Snap(footIK,footFKalign)
        
        cmds.parent(footFKalign,footIK)
        
        #setup controls
        mNode=mum.UpStream(ikPlug, 'module')
        cnts=mum.DownStream(mNode,'control')
        sockets=mum.DownStream(mNode,'socket')
        
        for cnt in cnts:
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
                data={'switch':footFKalign}
                mum.ModifyData(cnt, data)
                
                tn=mum.GetTransform(cnt)
                
                mru.Snap(tn,footFKalign,point=False)
        
        #attaching plug
        for socket in sockets:
            data=mum.GetData(socket)
            
            if data['index']=='3':
                tn=mum.GetTransform(socket)
                
                cmds.select(plug,tn,r=True)
                muz.attach()
                
                cmds.scaleConstraint(tn,plug)
        
        #parenting meta nodes
        cmds.connectAttr(mNode+'.message',module+'.metaParent')
        
        cnts=[ballCNT,toeIkCNT,toetipCNT,heelCNT,footCNT,toeFkCNT]
        
        for cnt in cnts:
            metaNode=mum.GetMetaNode(cnt)
            
            cmds.connectAttr(mNode+'.message',metaNode+'.metaParent',
                             force=True)
    else:
        pointCon=cmds.pointConstraint(footIK,footFK,footJNT)[0]
        
        cmds.connectAttr(fkikREV+'.outputX',
                         pointCon+'.'+footFK+'W1')
        cmds.connectAttr(asset+'.FKIK',
                         pointCon+'.'+footIK+'W0')
    
    #clean channel box
    cnts=[ballCNT,toeIkCNT,toetipCNT,heelCNT,footCNT,toeFkCNT]
    attrs=['tx','ty','tz','sx','sy','sz','v']
    
    for cnt in cnts:
        mru.ChannelboxClean(cnt, attrs)
    
    #publishing controllers
    for cnt in cnts:
        
        cmds.containerPublish(asset,publishNode=(cnt,''))
        cmds.containerPublish(asset,bindNode=(cnt,cnt))

'''
templateModule='meta_foot'
Rig(templateModule)
'''