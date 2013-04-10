import os

import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru
import Tapp.Maya.utils.ZvParentMaster as muz
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
                     namespace='limb')

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
        if mum.GetData(control)['component']=='start':
            start=mum.GetTransform(control)
        if mum.GetData(control)['component']=='mid':
            mid=mum.GetTransform(control)
        if mum.GetData(control)['component']=='end':
            end=mum.GetTransform(control)
    
    #getting transform data
    startTrans=cmds.xform(start,worldSpace=True,query=True,
                          translation=True)
    
    midTrans=cmds.xform(mid,worldSpace=True,query=True,
                        translation=True)
    
    endTrans=cmds.xform(end,worldSpace=True,query=True,
                        translation=True)
    endRot=cmds.xform(end,worldSpace=True,query=True,
                      rotation=True)
    
    #getting module data
    data=mum.GetData(module)
    
    upperTwist=data['upperTwist']
    upperTwistJoints=data['upperTwistJoints']
    
    lowerTwist=data['lowerTwist']
    lowerTwistJoints=data['lowerTwistJoints']
    
    limbType=data['limbType']
    
    fk=True
    ik=True
    
    #establish side
    side='center'
    
    x=(startTrans[0]+midTrans[0]+endTrans[0])/3
    
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
        data['index']==index and \
        data['component']==limbType:
            index+=1
    
    #delete template
    cmds.delete(cmds.container(q=True,fc=start))
    
    #establish prefix and suffix
    prefix=side[0]+'_'+limbType+str(index)+'_'
    suffix='_'+side[0]+'_'+limbType+str(index)
    
    #initial setup---
    
    #creating asset
    asset=cmds.container(n=prefix+'rig',type='dagContainer')
    
    #setup asset
    attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
    mru.ChannelboxClean(asset, attrs)
    
    #create module
    data={'side':side,'index':str(index),'system':'rig','subcomponent':limbType}
    
    module=mum.SetData(('meta'+suffix),'module','limb',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #create plug
    plug=cmds.spaceLocator(name=prefix+'plug')[0]
    
    metaParent=mum.SetData('meta_'+plug,'plug',None,module,
                            None)
    mum.SetTransform(plug, metaParent)
    
    cmds.container(asset,e=True,addNode=plug)
    
    #setup plug
    phgrp=cmds.group(empty=True,n=(plug+'_PH'))
    sngrp=cmds.group(empty=True,n=(plug+'_SN'))
    
    cmds.container(asset,e=True,addNode=[phgrp,sngrp])
    
    cmds.parent(sngrp,phgrp)
    cmds.parent(plug,sngrp)
    
    cmds.xform(phgrp,worldSpace=True,translation=startTrans)
    
    #create jnts---
    cmds.select(cl=True)
    startJoint=cmds.joint(name=prefix+'01_jnt')
    cmds.select(cl=True)
    midJoint=cmds.joint(name=prefix+'02_jnt')
    cmds.select(cl=True)
    endJoint=cmds.joint(name=prefix+'03_jnt')
    
    cmds.container(asset,e=True,addNode=[startJoint,midJoint,
                                         endJoint])
    
    #setup jnts
    cmds.xform(startJoint,ws=True,translation=startTrans)
    cmds.xform(midJoint,ws=True,translation=midTrans)
    cmds.xform(endJoint,ws=True,translation=endTrans)
    
    #finding the upVector for the joints
    crs=mru.CrossProduct(startTrans,midTrans,endTrans)
    
    #setup start joint
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=startTrans)
    cmds.aimConstraint(midJoint,grp,worldUpType='vector',
                       worldUpVector=crs)
    
    rot=cmds.xform(grp,query=True,rotation=True)
    cmds.rotate(rot[0],rot[1],rot[2],startJoint,
                worldSpace=True,pcp=True)
    
    mru.Snap(startJoint, plug)
    
    cmds.makeIdentity(startJoint,apply=True,t=1,r=1,s=1,n=0)
    
    cmds.delete(grp)
    
    #setup mid and end joint
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=midTrans)
    cmds.aimConstraint(endJoint,grp,worldUpType='vector',
                       worldUpVector=crs)
    
    rot=cmds.xform(grp,query=True,rotation=True)
    cmds.rotate(rot[0],rot[1],rot[2],midJoint,worldSpace=True,
                pcp=True)
    
    cmds.delete(grp)
    
    cmds.rotate(rot[0],rot[1],rot[2],endJoint,worldSpace=True,
                pcp=True)
    
    cmds.makeIdentity(midJoint,apply=True, t=1, r=1, s=1, n=0)
    cmds.makeIdentity(endJoint,apply=True, t=1, r=1, s=1, n=0)
    
    #setup end joint
    cmds.xform(endJoint,worldSpace=True,rotation=endRot)
    
    mru.ClosestOrient(midJoint, endJoint)
    
    #create socket
    startSocket=cmds.spaceLocator(name=prefix+'socket01')[0]
    midSocket=cmds.spaceLocator(name=prefix+'socket02')[0]
    endSocket=cmds.spaceLocator(name=prefix+'socket03')[0]
    
    cmds.container(asset,e=True,addNode=[startSocket,midSocket,
                                         endSocket])
    
    cmds.xform(startSocket,worldSpace=True,
               translation=startTrans)
    cmds.xform(midSocket,worldSpace=True,translation=midTrans)
    cmds.xform(endSocket,worldSpace=True,translation=endTrans)
    
    cmds.parent(startSocket,startJoint)
    cmds.parent(midSocket,midJoint)
    cmds.parent(endSocket,endJoint)
    
    data={'index':1}
    metaParent=mum.SetData('meta_'+startSocket,'socket',None,
                            module,data)
    mum.SetTransform(startSocket, metaParent)
    
    data={'index':2}
    metaParent=mum.SetData('meta_'+midSocket,'socket',None,
                            module,data)
    mum.SetTransform(midSocket, metaParent)
    
    data={'index':3}
    metaParent=mum.SetData('meta_'+endSocket,'socket',None,
                            module,data)
    mum.SetTransform(endSocket, metaParent)
    
    #create fk---
    if fk:
        startFkCNT=mru.Box(prefix+'startFk_cnt')
        midFkCNT=mru.Box(prefix+'midFk_cnt')
        endFkCNT=mru.Box(prefix+'endFk_cnt')
        
        cmds.container(asset,e=True,addNode=[startFkCNT,midFkCNT,endFkCNT])
        
        #setup startFkCNT
        data={'system':'fk','index':1}
        mNode=mum.SetData(('meta_'+startFkCNT),'control','start',
                           module,data)
        mum.SetTransform(startFkCNT, mNode)
        
        grp=cmds.group(startFkCNT,n=(startFkCNT+'_grp'))
        
        cmds.container(asset,e=True,addNode=grp)
        
        cmds.parent(grp,plug)
        
        mru.Snap(startJoint, grp)
        
        #setup midFkCNT
        data={'system':'fk','index':2}
        mNode=mum.SetData(('meta_'+midFkCNT),'control','mid',
                           module,data)
        mum.SetTransform(midFkCNT,mNode)
        
        grp=cmds.group(midFkCNT,n=(midFkCNT+'_grp'))
        cmds.container(asset,e=True,addNode=grp)
        
        cmds.parent(grp,startFkCNT)
        
        mru.Snap(midJoint, grp)
        
        #setup endFkCNT
        data={'system':'fk','index':3}
        mNode=mum.SetData(('meta_'+endFkCNT),'control','end',
                           module,data)
        mum.SetTransform(endFkCNT,mNode)
        
        grp=cmds.group(endFkCNT,n=(endFkCNT+'_grp'))
        cmds.container(asset,e=True,addNode=grp)
        
        cmds.parent(grp,midFkCNT)
        
        mru.Snap(endJoint, grp)
        
        #channelbox clean
        cnts=[startFkCNT,midFkCNT,endFkCNT]
        
        attrs=['sx','sy','sz']
        for cnt in cnts:
            mru.ChannelboxClean(cnt,attrs)
    
    #create ik---
    if ik:
        cmds.select(cl=True)
        startIk=cmds.joint(n=prefix+'ik01')
        midIk=cmds.joint(n=prefix+'ik02')
        endIk=cmds.joint(n=prefix+'ik03')
        
        cmds.container(asset,e=True,addNode=[startIk,midIk,endIk])
        
        #setup ik
        cmds.parent(startIk,plug)
        cmds.parent(midIk,startIk)
        cmds.parent(endIk,midIk)
        
        mru.Snap(startJoint,startIk)
        mru.Snap(midJoint,midIk)
        mru.Snap(endJoint,endIk)
        
        cmds.makeIdentity(startIk,apply=True,t=1,r=1,s=1,n=0)
        cmds.makeIdentity(midIk,apply=True,t=1,r=1,s=1,n=0)
        cmds.makeIdentity(endIk,apply=True,t=1,r=1,s=1,n=0)
        
        #create ik handle
        ikHandle=cmds.ikHandle(sj=startIk,ee=endIk,sol='ikRPsolver',
                               name=prefix+'ikHandle')
        
        cmds.container(asset,e=True,addNode=ikHandle[0])
        
        cmds.rename(ikHandle[1],prefix+'eff')
        
        #setup ik stretching
        stretch01=cmds.createNode('transform',ss=True,
                                  n=prefix+'stretch01')
        stretch02=cmds.createNode('transform',ss=True,
                                  n=prefix+'stretch02')
        stretch02REF=cmds.createNode('transform',ss=True,
                                  n=prefix+'stretch02REF')
        data={'system':'ik'}
        mNode=mum.SetData(('meta_'+stretch02REF),'plug',None,
                           module,data)
        mum.SetTransform(stretch02REF, mNode)
        
        stretchDIST=cmds.shadingNode('distanceBetween',
                                     asUtility=True,
                                     n=prefix+'stretchDIST')
        stretch01MD=cmds.shadingNode('multiplyDivide',
                                     asUtility=True,
                                     n=prefix+'stretch01MD')
        stretch02MD=cmds.shadingNode('multiplyDivide',
                                     asUtility=True,
                                     n=prefix+'stretch02MD')
        stretchBLD=cmds.shadingNode('blendColors',
                                    asUtility=True,
                                    n=prefix+'stretchBLD')
        
        phgrp=cmds.group(empty=True,n=(stretch02REF+'_PH'))
        sngrp=cmds.group(empty=True,n=(stretch02REF+'_SN'))
        
        cmds.container(asset,e=True,
                       addNode=[stretch01,stretch02,stretchDIST,
                                stretch01MD,stretch02MD,
                                stretchBLD,phgrp,sngrp,
                                stretch02REF])
        
        cmds.parent(sngrp,phgrp)
        cmds.parent(stretch02REF,sngrp)
        
        mru.Snap(endJoint,phgrp)
        mru.Snap(endJoint,stretch02)
        cmds.parentConstraint(stretch02REF,stretch02)
        
        cmds.scaleConstraint(plug,phgrp)
        
        cmds.transformLimits(startIk,sx=(1,1),esx=(1,0))
        cmds.transformLimits(midIk,sx=(1,1),esx=(1,0))
        
        temp1=mru.Distance(startJoint, midJoint)
        temp2=mru.Distance(midJoint,endJoint)
        
        cmds.setAttr('%s.color2R' % stretchBLD,1)
        cmds.setAttr('%s.blender' % stretchBLD,1)
        cmds.setAttr('%s.input2X' % stretch02MD,temp1+temp2)
        cmds.setAttr('%s.operation' % stretch01MD,2)
        
        cmds.pointConstraint(startIk,stretch01)
        cmds.xform(stretch02,worldSpace=True,translation=endTrans)
        
        cmds.parent(ikHandle[0],stretch02)
        
        cmds.connectAttr('%s.translate' % stretch01,
                         '%s.point1' % stretchDIST,force=True)
        cmds.connectAttr('%s.translate' % stretch02,
                         '%s.point2' % stretchDIST,force=True)
        
        cmds.connectAttr('%s.sx' % plug,'%s.input1X' % stretch02MD,
                         force=True)
        
        cmds.connectAttr('%s.distance' % stretchDIST,
                         '%s.input1X' % stretch01MD,force=True)
        cmds.connectAttr('%s.outputX' % stretch02MD,
                         '%s.input2X' % stretch01MD,force=True)
        
        cmds.connectAttr('%s.outputX' % stretch01MD,
                         '%s.color1R' % stretchBLD,force=True)
        
        cmds.connectAttr('%s.outputR' % stretchBLD,
                         '%s.sx' % startIk,force=True)
        cmds.connectAttr('%s.outputR' % stretchBLD,
                         '%s.sx' % midIk,force=True)
        
        #create controls
        polevectorCNT=mru.Sphere(prefix+'polevector_cnt')
        endIkCNT=mru.Sphere(prefix+'endIk_cnt')
        
        cmds.container(asset,e=True,addNode=[polevectorCNT,endIkCNT])
        
        #setup polevectorCNT
        data={'system':'ik','index':2}
        mNode=mum.SetData(('meta_'+polevectorCNT),'control',
                           'polevector', module,data)
        mum.SetTransform(polevectorCNT, mNode)
        
        cmds.xform(polevectorCNT,worldSpace=True,translation=midTrans)
        
        rot=cmds.xform(midJoint,worldSpace=True,q=True,
                       rotation=True)
        cmds.xform(polevectorCNT,worldSpace=True,rotation=rot)
        
        tx=mru.Distance(startJoint,midJoint)+mru.Distance(midJoint, endJoint)
        cmds.move(0,0,-tx/3,polevectorCNT,r=True,os=True,wd=True)
        
        phgrp=cmds.group(empty=True,n=(polevectorCNT+'_PH'))
        sngrp=cmds.group(empty=True,n=(polevectorCNT+'_SN'))
        
        cmds.container(asset,e=True,addNode=[phgrp,sngrp])
        
        cmds.delete(cmds.parentConstraint(polevectorCNT,phgrp))
        cmds.delete(cmds.parentConstraint(polevectorCNT,sngrp))
        
        cmds.parent(polevectorCNT,sngrp)
        cmds.parent(sngrp,phgrp)
        cmds.parent(phgrp,plug)
        
        curve=cmds.curve(d=1,p=[(0,0,0),(0,0,0)])
        polevectorSHP=cmds.listRelatives(curve,s=True)[0]
        cmds.setAttr(polevectorSHP+'.overrideEnabled',1)
        cmds.setAttr(polevectorSHP+'.overrideDisplayType',2)
        
        cmds.select(curve+'.cv[0]',r=True)
        cluster=mel.eval('newCluster " -envelope 1";')
        
        cmds.container(asset,e=True,addNode=[curve,cluster[0],
                                             cluster[1]])
        
        mru.Snap(polevectorCNT,cluster[1])
        cmds.parent(cluster[1],polevectorCNT)
        
        cmds.rename(cluster[0],prefix+'polvector_cls')
        
        cmds.select(curve+'.cv[1]',r=True)
        cluster=mel.eval('newCluster " -envelope 1";')
        
        cmds.container(asset,e=True,addNode=[cluster[0],
                                             cluster[1]])
        
        mru.Snap(midIk,cluster[1])
        cmds.parent(cluster[1],midIk)
        
        cmds.rename(cluster[0],prefix+'polvector_cls')
        polevectorSHP=cmds.rename(curve,prefix+'polevector_shp')
        
        cmds.poleVectorConstraint(polevectorCNT,ikHandle[0])
        
        #setup endIkCNT
        data={'system':'ik','index':1}
        mNode=mum.SetData(('meta_'+endIkCNT),'control','end',
                           module,data)
        mum.SetTransform(endIkCNT, mNode)
        
        grp=cmds.group(empty=True,n=(endIkCNT+'_grp'))
        phgrp=cmds.group(empty=True,n=(endIkCNT+'_PH'))
        sngrp=cmds.group(empty=True,n=(endIkCNT+'_SN'))
        
        cmds.container(asset,e=True,addNode=[grp,phgrp,sngrp])
        
        cmds.parent(grp,plug)
        cmds.parent(phgrp,grp)
        cmds.parent(sngrp,phgrp)
        cmds.parent(endIkCNT,sngrp)
        
        mru.Snap(endJoint,grp)
        
        cmds.select([stretch02REF,endIkCNT],r=True)
        muz.attach()
        
        #create individual controls
        ik01cnt=mru.Square(prefix+'ik01_cnt')
        ik02cnt=mru.Square(prefix+'ik02_cnt')
        ik03cnt=mru.Square(prefix+'ik03_cnt')
        
        #setup ik01cnt        
        data={'system':'ik','worldspace':'false',
              'index':3}
        mNode=mum.SetData(('meta_'+ik01cnt),'control',
                           'iktwist',module,data)
        mum.SetTransform(ik01cnt,mNode)
        
        mru.Snap(startIk,ik01cnt)
        
        cmds.parent(ik01cnt,startIk)
        
        #setup ik02cnt
        data={'system':'ik','worldspace':'false',
              'index':4}
        mNode=mum.SetData(('meta_'+ik02cnt),'control',
                           'iktwist',module,data)
        mum.SetTransform(ik02cnt,mNode)
        
        mru.Snap(midIk,ik02cnt)
        
        cmds.parent(ik02cnt,midIk)
        
        #setup ik02cnt
        data={'system':'ik','worldspace':'false',
              'index':5}
        mNode=mum.SetData(('meta_'+ik03cnt),'control',
                           'iktwist',module,data)
        mum.SetTransform(ik03cnt,mNode)
        
        mru.Snap(endIk,ik03cnt)
        
        cmds.parent(ik03cnt,endIkCNT)
        
        #channelbox clean
        cnts=[polevectorCNT,endIkCNT,ik01cnt,ik02cnt,ik03cnt]
        
        attrs=['sx','sy','sz']
        for cnt in cnts:
            mru.ChannelboxClean(cnt,attrs)
    
    #blending---
    if fk and ik:
        
        #create extra control
        extraCNT=mru.Pin(prefix+'extra_cnt')
        
        cmds.container(asset,e=True,addNode=extraCNT)
        
        #setup extra control
        mNode=mum.SetData(('meta_'+extraCNT),'control','extra',
                           module,None)
        mum.SetTransform(extraCNT,mNode)
        
        cmds.addAttr(extraCNT,ln='FKIK',at='float',keyable=True,
                     min=0,max=1)
        cmds.addAttr(extraCNT,ln='stretch',at='float',keyable=True,
                     min=0,max=1)
        
        cmds.connectAttr(extraCNT+'.stretch',stretchBLD+'.blender',
                         force=True)
        
        mru.Snap(endJoint,extraCNT)
        
        cmds.parent(extraCNT,endJoint)
        cmds.rotate(0,90,0,extraCNT,r=True,os=True)
        
        cmds.scaleConstraint(plug,extraCNT)
        
        #setup blending
        fkIkREV=cmds.shadingNode('reverse',asUtility=True,
                                 n=(prefix+'fkIkREV'))
        
        cmds.container(asset,e=True,addNode=[fkIkREV])
        
        cmds.connectAttr(extraCNT+'.FKIK',fkIkREV+'.inputX')
        
        con=cmds.parentConstraint(ik01cnt,startFkCNT,startJoint)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+
                         startFkCNT+'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+
                         ik01cnt+'W0',force=True)
        
        con=cmds.parentConstraint(ik02cnt,midFkCNT,midJoint)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+midFkCNT+
                         'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+
                         ik02cnt+'W0',force=True)
        
        con=cmds.parentConstraint(ik03cnt,endFkCNT,endJoint)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+endFkCNT+
                         'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+
                         ik03cnt+'W0',force=True)
        
        con=cmds.scaleConstraint(ik01cnt,startFkCNT,startJoint)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+
                         startFkCNT+'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+ik01cnt+
                         'W0',force=True)
        
        con=cmds.scaleConstraint(ik02cnt,midFkCNT,midJoint)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+
                         midFkCNT+'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+ik02cnt+
                         'W0',force=True)
        
        con=cmds.scaleConstraint(ik03cnt,endFkCNT,endJoint)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+
                         endFkCNT+'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+ik03cnt+
                         'W0',force=True)
        
        cmds.connectAttr(fkIkREV+'.outputX',startFkCNT+'.visibility')
        cmds.connectAttr(fkIkREV+'.outputX',midFkCNT+'.v')
        cmds.connectAttr(fkIkREV+'.outputX',endFkCNT+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',endIkCNT+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',polevectorCNT+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',polevectorSHP+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',ik01cnt+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',ik02cnt+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',ik03cnt+'.v')
        
        #setup switching
        data={'switch':ik01cnt}
        mum.ModifyData(startFkCNT, data)
        
        data={'switch':ik02cnt}
        mum.ModifyData(midFkCNT, data)
        
        data={'switch':ik03cnt}
        mum.ModifyData(endFkCNT, data)
        
        data={'switch':startFkCNT}
        mum.ModifyData(ik01cnt, data)
        
        data={'switch':midFkCNT}
        mum.ModifyData(ik02cnt, data)
        
        data={'switch':endFkCNT}
        mum.ModifyData(ik03cnt, data)
        
        data={'switch':endFkCNT}
        mum.ModifyData(endIkCNT, data)
        
        data={'switch':midFkCNT}
        mum.ModifyData(polevectorCNT, data)
        
        #channelbox clean
        attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
        mru.ChannelboxClean(extraCNT,attrs)
    
    #twist joints---
    tj=TwistJoints()
    if upperTwist=='True' or lowerTwist=='True':
        
        averageJNT=cmds.joint(p=[0,0,0],n=prefix+'average_jnt')
        
        cmds.container(asset,e=True,addNode=averageJNT)
        
        mru.Snap(midJoint,averageJNT)
        cmds.parent(averageJNT,midJoint)
        
        orientCon=cmds.orientConstraint(startJoint,midJoint,
                                        averageJNT)
        cmds.setAttr(orientCon[0]+'.interpType',2)
        
        cmds.addAttr(extraCNT,longName='bend',attributeType='float',
                     min=0,max=1,keyable=True,defaultValue=0)
        
        cmds.addAttr(extraCNT,longName='bendAmount',attributeType='float',
             min=0,keyable=True,defaultValue=1)
        
        bendRev=cmds.shadingNode('reverse',asUtility=True,
                                 n=(prefix+'bendRev'))
        
        cmds.connectAttr(extraCNT+'.bend',bendRev+'.inputX')
    
    if upperTwist=='True':
        result=tj.Rig(startJoint, midJoint, prefix+'upper_', int(upperTwistJoints),
                      asset, plug)
        
        cmds.parent(result['upvectors'][0],plug)
        cmds.parent(result['joints'][3],averageJNT)
        
        cmds.parentConstraint(midJoint,result['twistend'],mo=True)
        
        for loc in result['locators']:
            
            meta=mum.SetData('meta_'+loc, 'joint', None, module, None)
            mum.SetTransform(loc, meta)
        
        #bend amount
        cmds.scale(0.001,0.001,0.001,result['joints'][0])
        
        mru.Snap(midJoint,result['joints'][3])
        mru.Snap(midJoint,result['joints'][2])
        mru.Snap(startJoint,result['joints'][3],point=False)
        
        
        dist=mru.Distance(startJoint,midJoint)
        
        cmds.move(-dist/2,0,0,result['joints'][2],os=True)
        
        cmds.connectAttr(extraCNT+'.bendAmount',result['joints'][3]+'.sx')
        cmds.connectAttr(extraCNT+'.bendAmount',result['joints'][3]+'.sy')
        cmds.connectAttr(extraCNT+'.bendAmount',result['joints'][3]+'.sz')
        
        #bend control
        con=cmds.orientConstraint(averageJNT,startJoint,result['joints'][3])
        
        cmds.setAttr(con[0]+'.interpType',2)
        
        cmds.connectAttr(bendRev+'.outputX',con[0]+'.'+startJoint+
                         'W1',force=True)
        
        cmds.connectAttr(extraCNT+'.bend',con[0]+'.'+
                         averageJNT+'W0',force=True)
        
    else:
        meta=mum.SetData('meta_'+startJoint, 'joint', None, module, None)
        mum.SetTransform(startJoint, meta)
        
    if lowerTwist=='True':
        result=tj.Rig(midJoint,endJoint,prefix+'lower_', int(lowerTwistJoints),
                      asset, plug)
        
        cmds.parent(result['upvectors'][0],startJoint)
        cmds.parent(result['twiststartgrp'],startJoint)
        cmds.parent(result['twistendgrp'],startJoint)
        
        cmds.parentConstraint(midJoint,result['twiststart'],mo=True)
        cmds.parentConstraint(endJoint,result['twistend'],mo=True)
        
        cmds.move(0,0,-1,result['upvectors'][1],os=True)
        
        for loc in result['locators']:
            
            meta=mum.SetData('meta_'+loc, 'joint', None, module, None)
            mum.SetTransform(loc, meta)
        
        #bend Amount
        cmds.scale(0,0,0,result['joints'][3])
        
        mru.Snap(midJoint,result['joints'][0])
        mru.Snap(midJoint,result['joints'][1])
        
        dist=mru.Distance(startJoint,midJoint)
        
        cmds.move(dist/2,0,0,result['joints'][1],os=True)
        
        pms=cmds.shadingNode('plusMinusAverage',asUtility=True,
                             n=(prefix+'lower_pms'))
        
        cmds.addAttr(pms,ln='offset',at='float',keyable=True,defaultValue=0.001)
        
        cmds.connectAttr(pms+'.offset',pms+'.input1D[0]')
        cmds.connectAttr(extraCNT+'.bendAmount',pms+'.input1D[1]')
        
        cmds.connectAttr(pms+'.output1D',result['joints'][0]+'.sx')
        cmds.connectAttr(pms+'.output1D',result['joints'][0]+'.sy')
        cmds.connectAttr(pms+'.output1D',result['joints'][0]+'.sz')
        
        #bend control
        con=cmds.orientConstraint(averageJNT,midJoint,result['joints'][0])
        
        cmds.setAttr(con[0]+'.interpType',2)
        
        cmds.connectAttr(bendRev+'.outputX',con[0]+'.'+midJoint+
                         'W1',force=True)
        
        cmds.connectAttr(extraCNT+'.bend',con[0]+'.'+
                         averageJNT+'W0',force=True)
        
    else:
        meta=mum.SetData('meta_'+midJoint, 'joint', None, module, None) 
        mum.SetTransform(midJoint, meta)
        
    meta=mum.SetData('meta_'+endJoint, 'joint', None, module, None) 
    mum.SetTransform(endJoint, meta)

class TwistJoints():
    
    def Rig(self,startNode,endNode,prefix,jointAmount,asset,plug):
        ''' Creates twist joints from start to end. '''
        
        #return variable
        result={}
        
        #create curve
        startTrans=cmds.xform(startNode,ws=True,q=True,translation=True)
        endTrans=cmds.xform(endNode,ws=True,q=True,translation=True)
        
        curve=cmds.curve(d=1,p=[startTrans,endTrans],n=prefix+'ik_curve')
        
        cmds.container(asset,e=True,addNode=curve)
        
        #setup curve
        cmds.rebuildCurve(curve,rpo=1,rt=0,end=1,kr=0,kcp=0,kep=1,kt=0,s=1,d=2,tol=0.01)
        
        #create pathSpine
        pathSpine=mpps.MG_pathSpine(curve, jointAmount,skinCurve=True)
        
        #setup pathSpine
        for key in pathSpine:
            cmds.container(asset,e=True,addNode=pathSpine[key])
        
        cmds.delete(pathSpine['root'])
        del(pathSpine['root'])
        
        ikpathspine=cmds.rename(pathSpine['MG_pathSpine'],prefix+'ik_pathSpine')
        
        result['pathspine']=ikpathspine
        
        cmds.rename(pathSpine['vector'],prefix+'ik_vector')
        
        iktwistend=cmds.rename(pathSpine['twist_end'],prefix+'ik_twistend')
        iktwiststart=cmds.rename(pathSpine['twist_start'],prefix+'ik_twiststart')
        
        result['twistend']=iktwistend
        result['twiststart']=iktwiststart
        
        ikupvectors=[]
        for item in pathSpine['up_vector']:
            
            item=cmds.rename(item,prefix+'ik_upvector1')
            
            ikupvectors.append(item)
        
        result['upvectors']=ikupvectors
        
        iklocators=[]
        for item in pathSpine['locators']:
            
            item=cmds.rename(item,prefix+'ik_loc1')
            
            iklocators.append(item)
        
        result['locators']=iklocators
        
        ikjoints=[]
        for item in pathSpine['joints']:
            
            item=cmds.rename(item,prefix+'ik_jnt1')
            
            ikjoints.append(item)
        
        result['joints']=ikjoints
        
        cmds.setAttr(ikpathspine+'.keepTwistVolume',0)
        cmds.connectAttr(plug+'.sx',ikpathspine+'.globalScale')
        
        cmds.parent(ikupvectors[0],plug)
        cmds.parent(ikupvectors[1],ikupvectors[0])
        
        #setup twist  
        twiststartgrp=cmds.group(empty=True,n=prefix+'ik_twiststart_grp')
        twistendgrp=cmds.group(empty=True,n=prefix+'ik_twistend_grp')
        
        result['twiststartgrp']=twiststartgrp
        result['twistendgrp']=twistendgrp
        
        cmds.container(asset,e=True,addNode=twiststartgrp)
        cmds.container(asset,e=True,addNode=twistendgrp)
        
        mru.Snap(iktwiststart,twiststartgrp)
        mru.Snap(iktwistend,twistendgrp)
        
        cmds.parent(iktwiststart,twiststartgrp)
        cmds.parent(iktwistend,twistendgrp)
              
        cmds.parent(twiststartgrp,plug)
        cmds.parent(twistendgrp,plug)
        
        #setup bend control
        cmds.parent(ikjoints[1],ikjoints[0])
        
        cmds.parent(ikjoints[2],ikjoints[3])
        
        cmds.parent(ikjoints[0],startNode)
        cmds.parent(ikjoints[3],endNode)
        
        cmds.parent(ikupvectors[0],startNode)
        
        #return
        return result

#module='limb:meta_limb'
#Rig(module)