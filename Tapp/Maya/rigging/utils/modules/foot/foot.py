import maya.cmds as cmds

from Tapp.Maya import utils as mu
from Tapp.Maya.rigging.utils import utils as mru
from Tapp.Maya.utils import ZvParentMaster as zv

class Foot():
    ''' Class for all foot module related functions. '''
    
    def Create(self):
        ''' Create or Imports the template module to rig '''
        pass
    
    def Attach(self,sourceModule,targetModule):
        pass
    
    def Detach(self,module):
        pass
    
    def Rig(self,module):
        ''' Rigs the provided module. '''
        
        #class variables
        meta=mu.meta.Meta()
        ut=mru.Transform()
        ucs=mru.ControlShape()
        um=mru.Math()
        
        #collect all components
        controls=meta.DownStream(module,'control')
        
        for control in controls:
            data=meta.GetData(control)
            
            if data['component']=='foot':
                foot=meta.GetTransform(control)
            if data['component']=='toe':
                toe=meta.GetTransform(control)
            if data['component']=='toetip':
                toetip=meta.GetTransform(control)
            if data['component']=='heel':
                heel=meta.GetTransform(control)
            if data['component']=='bank' and data['side']=='right':
                rbank=meta.GetTransform(control)
            if data['component']=='bank' and data['side']=='left':
                lbank=meta.GetTransform(control)
        
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
        data=meta.GetData(module)
        
        attachToLeg=data['attachToLeg']
        
        #establish side
        side='center'
        
        x=(footTrans[0]+toetipTrans[0]+heelTrans[0])/3
        
        if x>1.0:
            side='left'
        if x<-1.0:
            side='right'
        
        #establish index
        data=meta.GetData(module)
        
        index=data['index']
        
        for node in cmds.ls(type='network'):
            data=meta.GetData(node)
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
        
        module=meta.SetData(('meta'+suffix),'module','foot',None,
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
        
        #create plug
        plug=cmds.spaceLocator(name=prefix+'plug')[0]
        
        phgrp=cmds.group(plug,n=(plug+'_PH'))
        sngrp=cmds.group(plug,n=(plug+'_SN'))
        
        cmds.xform(phgrp,worldSpace=True,translation=footTrans)
        
        metaParent=meta.SetData('meta_'+plug,'plug',None,module,
                                None)
        
        meta.SetTransform(plug, metaParent)
        
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
        metaParent=meta.SetData('meta_'+socket01,'socket',None,
                                module,data)
        meta.SetTransform(socket01, metaParent)
        data={'index':2}
        metaParent=meta.SetData('meta_'+socket02,'socket',None,
                                module,data)
        meta.SetTransform(socket02, metaParent)
        
        cmds.container(asset,e=True,addNode=[socket01,socket02])
        
        #finding the upVector for the joints
        crs=um.CrossProduct(footTrans,toeTrans,toetipTrans)
        
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
        
        ballCNT=ucs.Circle(prefix+'ball_cnt')
        toeIkCNT=ucs.Circle(prefix+'toeIk_cnt')
        toetipCNT=ucs.Sphere(prefix+'toetip_cnt')
        heelCNT=ucs.Sphere(prefix+'heel_cnt')
        footCNT=ucs.Sphere(prefix+'foot_cnt')
        toeFkCNT=ucs.Square(prefix+'toeFk_cnt')
        
        cmds.container(asset,e=True,addNode=[ballCNT,toeIkCNT,
                                             toetipCNT,heelCNT,
                                             footCNT,toeFkCNT,
                                             zeroCNT])
        
        #create right bank
        rbankGRP=cmds.group(empty=True,n=prefix+'r_bank_grp')
        
        cmds.container(asset,e=True,addNode=[rbankGRP])
        
        #setup right bank
        rbankParent=cmds.group(rbankGRP,n=rbankGRP+'_grp')
        phgrp=cmds.group(rbankParent,n=(rbankParent+'_PH'))
        sngrp=cmds.group(rbankParent,n=(rbankParent+'_SN'))
        
        cmds.xform(rbankParent,ws=True,translation=rbankTrans)
        cmds.xform(rbankParent,ws=True,rotation=rbankRot)
        
        cmds.rotate(-90,0,0,rbankParent,r=True,os=True)
        cmds.rotate(0,0,-90,rbankParent,r=True,os=True)
        
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
        data={'system':'ik','switch':zeroCNT}
        mNode=meta.SetData(('meta_'+heelCNT),'control','heel',
                           module,data)
        meta.SetTransform(heelCNT, mNode)
        
        heelGRP=cmds.group(heelCNT,n=(heelCNT+'_grp'))
        grp=cmds.group(heelGRP,n=(heelGRP+'_grp'))
        
        cmds.xform(grp,ws=True,rotation=heelRot)
        cmds.xform(grp,ws=True,translation=heelTrans)
        
        cmds.rotate(-90,0,0,grp,r=True,os=True)
        cmds.rotate(0,0,-90,grp,r=True,os=True)
        
        cmds.parent(grp,lbankGRP)
        
        cmds.container(asset,e=True,addNode=[heelGRP,grp])
        
        #setup toetipCNT
        data={'system':'ik','switch':zeroCNT}
        mNode=meta.SetData(('meta_'+toetipCNT),'control','toetip',
                           module,data)
        meta.SetTransform(toetipCNT, mNode)
        
        toetipGRP=cmds.group(toetipCNT,n=(toetipCNT+'_grp'))
        grp=cmds.group(toetipGRP,n=(toetipGRP+'_grp'))
        
        cmds.xform(grp,ws=True,rotation=heelRot)
        cmds.xform(grp,ws=True,translation=toetipTrans)
        
        cmds.parent(grp,heelCNT)
        
        cmds.rotate(-90,0,0,grp,r=True,os=True)
        cmds.rotate(0,0,-90,grp,r=True,os=True)
        
        cmds.container(asset,e=True,addNode=[toetipGRP,grp])
        
        #setup ballCNT
        data={'system':'ik','switch':zeroCNT}
        mNode=meta.SetData(('meta_'+ballCNT),'control','ball',
                           module,data)
        meta.SetTransform(ballCNT, mNode)
        
        cmds.scale(1.5,1.5,1.5,ballCNT)
        cmds.makeIdentity(ballCNT,apply=True, t=1, r=1, s=1, n=0)
        
        ballGRP=cmds.group(ballCNT,n=(ballCNT+'_grp'))
        grp=cmds.group(ballGRP,n=ballGRP+'_grp')
        
        ut.Snap(toeJNT,grp)
        
        cmds.parent(grp,toetipCNT)
        
        cmds.container(asset,e=True,addNode=[ballGRP,grp])
        
        #setup toeIkCNT
        data={'system':'ik','switch':toeFK}
        mNode=meta.SetData(('meta_'+toeIkCNT),'control','toe',
                           module,data)
        meta.SetTransform(toeIkCNT, mNode)
        
        toeIkGRP=cmds.group(toeIkCNT,n=(toeIkCNT+'_grp'))
        grp=cmds.group(toeIkGRP,n=(toeIkGRP+'_grp'))
        
        ut.Snap(toeJNT,grp)
        
        cmds.parent(grp,toetipCNT)
        
        cmds.container(asset,e=True,addNode=[toeIkGRP,grp])
        
        #setup footCNT
        data={'system':'ik','switch':zeroCNT}
        mNode=meta.SetData(('meta_'+footCNT),'control','foot',
                           module,data)
        meta.SetTransform(footCNT, mNode)
        
        grp=cmds.group(footCNT,n=(footCNT+'_grp'))
        cmds.parent(grp,rbankParent)
        
        cmds.xform(grp,ws=True,rotation=heelRot)
        cmds.xform(grp,ws=True,translation=heelTrans)
        cmds.move(0,0,-2,grp,r=True,os=True)
        
        cmds.rotate(-90,0,0,grp,r=True,os=True)
        cmds.rotate(0,0,-90,grp,r=True,os=True)
        
        cmds.container(asset,e=True,addNode=[grp])
        
        #setup toeFkCNT
        data={'system':'fk','switch':toeIK}
        mNode=meta.SetData(('meta_'+toeFkCNT),'control','toe',
                           module,data)
        meta.SetTransform(toeFkCNT, mNode)
        
        grp=cmds.group(toeFkCNT,n=(toeFkCNT+'_grp'))
        cmds.parent(grp,plug)
        
        ut.Snap(toeJNT,grp)
        
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
                data=meta.GetData(node)
                if data['type']=='module' and \
                data['component']=='limb':
                    nodes=meta.DownStream(node,'plug')
                    for n in nodes:
                        data=meta.GetData(n)
                        if 'system' in data:
                            tn=meta.GetTransform(n)
                            plugs[tn]=um.Distance(tn, plug)
            
            #attaching ik plug
            ikPlug=min(plugs, key=plugs.get)
            
            cmds.select(ikPlug,r=True)
            zv.detach()
            
            cmds.select(ikPlug,ballCNT,r=True)
            zv.attach()
            
            #setup controls
            mNode=meta.UpStream(ikPlug, 'module')
            cnts=meta.DownStream(mNode,'control')
            sockets=meta.DownStream(mNode,'socket')
            
            for cnt in cnts:
                data=meta.GetData(cnt)
                
                #setup ik control
                if 'system' in data and data['system']=='ik' \
                and data['component']=='end':
                    tn=meta.GetTransform(cnt)
                    
                    cmds.select(rbankParent,tn,r=True)
                    zv.attach()
                
                #setup extra control
                if data['component']=='extra':
                    tn=meta.GetTransform(cnt)
                    
                    cmds.connectAttr(tn+'.FKIK',asset+'.FKIK')
            
            #attaching plug
            for socket in sockets:
                data=meta.GetData(socket)
                
                if data['index']=='3':
                    tn=meta.GetTransform(socket)
                    
                    cmds.select(plug,tn,r=True)
                    zv.attach()
            
            #parenting meta nodes
            cmds.connectAttr(mNode+'.message',module+'.metaParent')
        else:
            pointCon=cmds.pointConstraint(footIK,footFK,footJNT)[0]
            
            cmds.connectAttr(fkikREV+'.outputX',
                             pointCon+'.'+footFK+'W1')
            cmds.connectAttr(footCNT+'.FKIK',
                             pointCon+'.'+footIK+'W0')

templateModule='meta_foot'

foot=Foot()
foot.Rig(templateModule)