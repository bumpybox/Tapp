import os

import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru
import Tapp.Maya.utils.ZvParentMaster as muz

def Create():
    ''' Imports the template module to rig.
        returns imported nodes.
    '''
    
    path=os.path.realpath(__file__)
    
    filePath=path.replace('\\','/').split('.')[0]+'.ma'
    
    return cmds.file(filePath,i=True,defaultNamespace=True,
                     returnNewNodes=True)

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
    
    tj=TwistJoints()
    
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
    
    #establish side
    side='center'
    
    x=(startTrans[0]+midTrans[0]+endTrans[0])/3
    
    if x>1.0:
        side='left'
    if x<-1.0:
        side='right'
    
    #establish index
    data=mum.GetData(module)
    
    index=data['index']
    
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
    
    #creating asset
    asset=cmds.container(n=prefix+'rig')
    
    #create module
    data={'side':side,'index':str(index),'system':'rig'}
    
    module=mum.SetData(('meta'+suffix),'module','limb',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #create joints
    startJoint=cmds.joint(position=(startTrans[0],
                                    startTrans[1],
                                    startTrans[2]),
                          name=prefix+'jnt01')
    midJoint=cmds.joint(position=(midTrans[0],midTrans[1],
                                  midTrans[2]),
                        name=prefix+'jnt02')
    endJoint=cmds.joint(position=(endTrans[0],endTrans[1],
                                  endTrans[2]),
                        name=prefix+'jnt03')
    
    cmds.container(asset,e=True,addNode=[startJoint,midJoint,
                                         endJoint])
    
    #create plug
    plug=cmds.spaceLocator(name=prefix+'plug')[0]
    
    phgrp=cmds.group(plug,n=(plug+'_PH'))
    sngrp=cmds.group(plug,n=(plug+'_SN'))
    
    cmds.xform(phgrp,worldSpace=True,translation=startTrans)
    
    metaParent=mum.SetData('meta_'+plug,'plug',None,module,
                            None)
    
    mum.SetTransform(plug, metaParent)
    
    cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
    
    #create socket
    startSocket=cmds.spaceLocator(name=prefix+'socket01')[0]
    midSocket=cmds.spaceLocator(name=prefix+'socket02')[0]
    endSocket=cmds.spaceLocator(name=prefix+'socket03')[0]
    
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
    
    cmds.container(asset,e=True,addNode=[startSocket,midSocket,
                                         endSocket])
    
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
    
    cmds.parent(startJoint,plug)
    
    cmds.makeIdentity(startJoint,apply=True,t=1,r=1,s=1,n=0)
    
    cmds.delete(grp)
    
    #setup mid and end blend
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
    
    #create ik chain
    startIk=cmds.duplicate(startJoint,st=True,po=True,
                           n=prefix+'ik01')[0]
    midIk=cmds.duplicate(midJoint,st=True,po=True,
                         n=prefix+'ik02')[0]
    endIk=cmds.duplicate(endJoint,st=True,po=True,
                         n=prefix+'ik03')[0]
    
    cmds.parent(midIk,startIk)
    cmds.parent(endIk,midIk)
    
    cmds.connectAttr('%s.scale' % startIk,
                     '%s.inverseScale' % midIk,force=True)
    cmds.connectAttr('%s.scale' % midIk,
                     '%s.inverseScale' % endIk,force=True)
    
    cmds.container(asset,e=True,addNode=[startIk,midIk,endIk])
    
    #create polevector
    polevector=cmds.spaceLocator(name=prefix+'polevector')[0]
    cmds.xform(polevector,worldSpace=True,translation=midTrans)
    
    rot=cmds.xform(midJoint,worldSpace=True,q=True,
                   rotation=True)
    cmds.xform(polevector,worldSpace=True,rotation=rot)
    
    tx=cmds.getAttr('%s.tx' % midJoint)
    cmds.move(0,0,-tx,polevector,r=True,os=True,wd=True)
    
    cmds.container(asset,e=True,addNode=[polevector])
    
    #create ik handle
    ikHandle=cmds.ikHandle(sj=startIk,ee=endIk,
                           sol='ikRPsolver',
                           name=prefix+'ikHandle')
    
    cmds.container(asset,e=True,addNode=[ikHandle[0],
                                         ikHandle[1]])
    
    cmds.rename(ikHandle[1],prefix+'_eff')
    
    cmds.poleVectorConstraint(polevector,ikHandle[0])
    
    #create fk chain
    startFk=cmds.duplicate(startJoint,st=True,po=True,
                           n=prefix+'fk01')[0]
    midFk=cmds.duplicate(midJoint,st=True,po=True,
                         n=prefix+'fk02')[0]
    endFk=cmds.duplicate(endJoint,st=True,po=True,
                         n=prefix+'fk03')[0]
    
    rot=cmds.xform(endJoint,worldSpace=True,q=True,
                   rotation=True)
    cmds.xform(endFk,worldSpace=True,rotation=rot)
    
    cmds.parent(midFk,startFk)
    cmds.parent(endFk,midFk)
    
    cmds.container(asset,e=True,addNode=[startFk,midFk,endFk])
    
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
    
    phgrp=cmds.group(stretch02REF,n=(stretch02REF+'_PH'))
    sngrp=cmds.group(stretch02REF,n=(stretch02REF+'_SN'))
    
    mru.Snap(endJoint,phgrp)
    mru.Snap(endJoint,stretch02)
    cmds.pointConstraint(stretch02REF,stretch02)
    
    cmds.scaleConstraint(plug,phgrp)
    
    cmds.container(asset,e=True,
                   addNode=[stretch01,stretch02,stretchDIST,
                            stretch01MD,stretch02MD,
                            stretchBLD,phgrp,sngrp,
                            stretch02REF])
    
    cmds.transformLimits(startIk,sx=(1,1),esx=(1,0))
    cmds.transformLimits(midIk,sx=(1,1),esx=(1,0))
    
    temp1=cmds.getAttr('%s.tx' % midJoint)
    temp2=cmds.getAttr('%s.tx' % endJoint)
    
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
    
    #creating controls       
    polevectorCNT=mru.Sphere(prefix+'polevector_cnt')
    endIkCNT=mru.Sphere(prefix+'endIk_cnt')
    startFkCNT=mru.Box(prefix+'startFk_cnt')
    midFkCNT=mru.Box(prefix+'midFk_cnt')
    endFkCNT=mru.Box(prefix+'endFk_cnt')
    extraCNT=mru.Pin(prefix+'extra_cnt')
    
    cnts=[polevectorCNT,endIkCNT,startFkCNT,midFkCNT,endFkCNT,
          extraCNT]
    
    #setup polevectorCNT
    data={'system':'ik','switch':midFk,'index':2}
    mNode=mum.SetData(('meta_'+polevectorCNT),'control',
                       'polevector', module,data)
    mum.SetTransform(polevectorCNT, mNode)
    
    grp=cmds.group(polevectorCNT,n=(polevectorCNT+'_grp'))
    cmds.parent(grp,plug)
    
    phgrp=cmds.group(polevectorCNT,n=(polevectorCNT+'_PH'))
    sngrp=cmds.group(polevectorCNT,n=(polevectorCNT+'_SN'))
    
    mru.Snap(polevector,grp)
    
    cmds.parent(polevector,polevectorCNT)
    
    cmds.container(asset,e=True,addNode=[grp,phgrp,sngrp])
    
    curve=cmds.curve(d=1,p=[(0,0,0),(0,0,0)])
    polevectorSHP=cmds.listRelatives(curve,s=True)[0]
    cmds.setAttr(polevectorSHP+'.overrideEnabled',1)
    cmds.setAttr(polevectorSHP+'.overrideDisplayType',2)
    
    cmds.select(curve+'.cv[0]',r=True)
    cluster=mel.eval('newCluster " -envelope 1";')
    mru.Snap(polevector,cluster[1])
    cmds.parent(cluster[1],polevector)
    
    cmds.container(asset,e=True,addNode=[curve,cluster[0],
                                         cluster[1]])
    cmds.rename(cluster[0],prefix+'polvector_cls')
    
    cmds.select(curve+'.cv[1]',r=True)
    cluster=mel.eval('newCluster " -envelope 1";')
    mru.Snap(midIk,cluster[1])
    cmds.parent(cluster[1],midIk)
    
    cmds.container(asset,e=True,addNode=[cluster[0],
                                         cluster[1]])
    cmds.rename(cluster[0],prefix+'polvector_cls')
    polevectorSHP=cmds.rename(curve,prefix+'polevector_shp')
    
    #setup endIkCNT
    data={'system':'ik','switch':endFk,'index':1}
    mNode=mum.SetData(('meta_'+endIkCNT),'control','end',
                       module,data)
    mum.SetTransform(endIkCNT, mNode)
    
    grp=cmds.group(endIkCNT,n=(endIkCNT+'_grp'))
    cmds.parent(grp,plug)
    
    phgrp=cmds.group(endIkCNT,n=(endIkCNT+'_PH'))
    sngrp=cmds.group(endIkCNT,n=(endIkCNT+'_SN'))
    
    mru.Snap(endFk,grp)
    
    cmds.select([stretch02REF,endIkCNT],r=True)
    muz.attach()
    
    cmds.container(asset,e=True,addNode=[grp,phgrp,sngrp])
    
    #setup startFkCNT
    data={'system':'fk','switch':startIk,'index':1}
    mNode=mum.SetData(('meta_'+startFkCNT),'control','start',
                       module,data)
    mum.SetTransform(startFkCNT, mNode)
    
    grp=cmds.group(startFkCNT,n=(startFkCNT+'_grp'))
    cmds.parent(grp,plug)
    
    mru.Snap(startFk, grp)
    
    cmds.parent(startFk,startFkCNT)
    
    cmds.container(asset,e=True,addNode=grp)
    
    #setup midFkCNT
    data={'system':'fk','switch':midIk,'index':2}
    mNode=mum.SetData(('meta_'+midFkCNT),'control','mid',
                       module,data)
    mum.SetTransform(midFkCNT,mNode)
    
    grp=cmds.group(midFkCNT,n=(midFkCNT+'_grp'))
    cmds.parent(grp,startFk)
    
    mru.Snap(midFk, grp)
    
    cmds.parent(midFk,midFkCNT)
    
    cmds.container(asset,e=True,addNode=grp)
    
    #setup endFkCNT
    data={'system':'fk','switch':endIkCNT,'index':3}
    mNode=mum.SetData(('meta_'+endFkCNT),'control','end',
                       module,data)
    mum.SetTransform(endFkCNT,mNode)
    
    grp=cmds.group(endFkCNT,n=(endFkCNT+'_grp'))
    cmds.parent(grp,midFk)
    
    mru.Snap(endFk, grp)
    
    cmds.parent(endFk,endFkCNT)
    
    cmds.container(asset,e=True,addNode=grp)
    
    #setup extraCNT
    mNode=mum.SetData(('meta_'+extraCNT),'control','extra',
                       module,None)
    mum.SetTransform(extraCNT,mNode)
    
    cmds.addAttr(extraCNT,ln='FKIK',at='float',keyable=True,
                 min=0,max=1)
    cmds.addAttr(extraCNT,ln='ikTwistControls',at='float',
                 keyable=True,min=0,max=1)
    cmds.addAttr(extraCNT,ln='stretch',at='float',keyable=True,
                 min=0,max=1)
    
    cmds.connectAttr(extraCNT+'.stretch',stretchBLD+'.blender',
                     force=True)
    
    mru.Snap(endFk,extraCNT)
    
    cmds.parent(extraCNT,endJoint)
    cmds.rotate(0,90,0,extraCNT,r=True,os=True)
    
    cmds.scaleConstraint(plug,extraCNT)
    
    #create twist controls
    startIkTwistCNT=mru.Circle(prefix+'startIkTwist_cnt')
    midIkTwistCNT=mru.Circle(prefix+'midIkTwist_cnt')
    
    cnts.append(startIkTwistCNT)
    cnts.append(midIkTwistCNT)
    
    #create twist joints
    startIkTwistJNT=cmds.duplicate(startIk,st=True,po=True,
                                   n=(prefix+'ikTwist01'))[0]
    midIkTwistJNT=cmds.duplicate(midIk,st=True,po=True,
                                 n=(prefix+'ikTwist02'))[0]
    
    cmds.container(asset,e=True,addNode=[startIkTwistJNT,
                                         midIkTwistJNT])
    
    #setup startIkTwistCNT        
    data={'system':'ik','switch':startFk,'worldspace':'false',
          'index':1}
    mNode=mum.SetData(('meta_'+startIkTwistCNT),'control',
                       'iktwist',module,data)
    mum.SetTransform(startIkTwistCNT,mNode)
    
    mru.Snap(startIk,startIkTwistCNT)
    
    cmds.parent(startIkTwistJNT,startIkTwistCNT)
    cmds.parent(startIkTwistCNT,startIk)
    
    #setup midIkTwistCNT
    data={'system':'ik','switch':midFk,'worldspace':'false',
          'index':2}
    mNode=mum.SetData(('meta_'+midIkTwistCNT),'control',
                       'iktwist',module,data)
    mum.SetTransform(midIkTwistCNT,mNode)
    
    mru.Snap(midIk,midIkTwistCNT)
    
    cmds.parent(midIkTwistJNT,midIkTwistCNT)
    cmds.parent(midIkTwistCNT,midIk)
    
    #setup blending
    fkIkREV=cmds.shadingNode('reverse',asUtility=True,
                             n=(prefix+'fkIkREV'))
    
    cmds.container(asset,e=True,addNode=[fkIkREV])
    
    cmds.connectAttr(extraCNT+'.FKIK',fkIkREV+'.inputX')
    
    orientCon=cmds.orientConstraint(startIkTwistJNT,startFk,
                                    startJoint)
    cmds.setAttr(orientCon[0]+'.interpType',2)
    cmds.connectAttr(fkIkREV+'.outputX',orientCon[0]+'.'+
                     startFk+'W1',force=True)
    cmds.connectAttr(extraCNT+'.FKIK',orientCon[0]+'.'+
                     startIkTwistJNT+'W0',force=True)
    orientCon=cmds.orientConstraint(midIkTwistJNT,midFk,
                                    midJoint)
    cmds.setAttr(orientCon[0]+'.interpType',2)
    cmds.connectAttr(fkIkREV+'.outputX',orientCon[0]+'.'+midFk+
                     'W1',force=True)
    cmds.connectAttr(extraCNT+'.FKIK',orientCon[0]+'.'+
                     midIkTwistJNT+'W0',force=True)
    orientCon=cmds.orientConstraint(stretch02,endFk,endJoint)
    cmds.setAttr(orientCon[0]+'.interpType',2)
    cmds.connectAttr(fkIkREV+'.outputX',orientCon[0]+'.'+endFk+
                     'W1',force=True)
    cmds.connectAttr(extraCNT+'.FKIK',orientCon[0]+'.'+
                     stretch02+'W0',force=True)
    scaleCon=cmds.scaleConstraint(startIk,startFk,startJoint)
    cmds.connectAttr(fkIkREV+'.outputX',scaleCon[0]+'.'+
                     startFk+'W1',force=True)
    cmds.connectAttr(extraCNT+'.FKIK',scaleCon[0]+'.'+startIk+
                     'W0',force=True)
    
    cmds.connectAttr(startJoint+'.sx',midJoint+'.sx',
                     force=True)
    
    cmds.connectAttr(fkIkREV+'.outputX',startFkCNT+
                     '.visibility')
    cmds.connectAttr(fkIkREV+'.outputX',midFkCNT+'.v')
    cmds.connectAttr(fkIkREV+'.outputX',endFkCNT+'.v')
    cmds.connectAttr(extraCNT+'.FKIK',endIkCNT+'.v')
    cmds.connectAttr(extraCNT+'.FKIK',polevectorCNT+'.v')
    cmds.connectAttr(extraCNT+'.FKIK',polevectorSHP+'.v')
    cmds.connectAttr(extraCNT+'.ikTwistControls',
                     startIkTwistCNT+'.v')
    cmds.connectAttr(extraCNT+'.ikTwistControls',
                     midIkTwistCNT+'.v')
    
    #twist joints        
    if upperTwist==True or lowerTwist==True:
        averageJNT=cmds.joint(p=[0,0,0],n=prefix+'average_jnt')
        
        mru.Snap(midFk,averageJNT)
        cmds.parent(averageJNT,midJoint)
        
        orientCon=cmds.orientConstraint(startJoint,midJoint,
                                        averageJNT)
        cmds.setAttr(orientCon[0]+'.interpType',2)
        
        cmds.container(asset,e=True,addNode=[averageJNT])
    
    if upperTwist==True:
        nodes=tj.Rig(startJoint,averageJNT,plug,midJoint,
                     averageJNT,extraCNT,plug,upperTwistJoints,
                     prefix+'upper_',module)
        
        for node in nodes:
                cmds.container(asset,e=True,
                               addNode=[node,node])
    else:
        meta=mum.SetData('meta_'+startJoint, 'joint', None, module, None)
        mum.SetTransform(startJoint, meta)
        
    if lowerTwist==True:
        nodes=tj.Rig(midJoint,endJoint,midJoint,endJoint,
                     averageJNT,extraCNT,plug,lowerTwistJoints,
                     prefix+'lower_',module)
        
        for node in nodes:
                cmds.container(asset,e=True,
                               addNode=[node,node])
    else:
        meta=mum.SetData('meta_'+midJoint, 'joint', None, module, None) 
        mum.SetTransform(midJoint, meta)
        
        meta=mum.SetData('meta_'+endJoint, 'joint', None, module, None) 
        mum.SetTransform(endJoint, meta)
    
    #channelbox cleanup
    attrs=['rx','ry','rz','sx','sy','sz','v']
    mru.ChannelboxClean(polevectorCNT, attrs)
    
    attrs=['sx','sy','sz','v']
    mru.ChannelboxClean(endIkCNT, attrs)
    
    attrs=['v']
    mru.ChannelboxClean(startFkCNT, attrs)
    mru.ChannelboxClean(midFkCNT, attrs)
    mru.ChannelboxClean(endFkCNT, attrs)
    
    attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
    mru.ChannelboxClean(extraCNT, attrs)
    
    attrs=['tx','ty','tz','ry','rz','sx','sy','sz','v']
    mru.ChannelboxClean(startIkTwistCNT, attrs)
    mru.ChannelboxClean(midIkTwistCNT, attrs)
    
    #publishing controllers
    for cnt in cnts:
        cmds.container(asset,e=True,addNode=[cnt])
        cmds.containerPublish(asset,publishNode=(cnt,''))
        cmds.containerPublish(asset,bindNode=(cnt,cnt))

class TwistJoints():
    
    def Rig(self,start,end,startMatrix,endMatrix,bendControl,
            attrControl,scaleRoot,amount,prefix,module):
        ''' Creates twist joints from start to end. '''
        
        #clear selection
        cmds.select(cl=True)
        
        #nodes collection
        nodes=[]
        
        #calculate distance
        startPOS=cmds.xform(start,q=True,translation=True,ws=True)
        endPOS=cmds.xform(end,q=True,translation=True,ws=True)
        
        distX=startPOS[0]-endPOS[0]
        distY=startPOS[1]-endPOS[1]
        distZ=startPOS[2]-endPOS[2]
        
        dist=mel.eval('mag <<%s,%s,%s>>;' % (distX,distY,distZ))
        
        #create joints
        jnts=[]
        
        for count in xrange(0,amount+1):
            jnt=cmds.joint(p=((dist/amount)*count,0,0),
                           n=prefix+'twist'+str(count))
            
            jnts.append(jnt)
            nodes.append(jnt)
        
        mru.Snap(start, jnts[0])
        
        #setup joints
        for jnt in jnts:
            meta=mum.SetData('meta_'+jnt, 'joint', None, module, None)
            mum.SetTransform(jnt, meta)
        
        ikHandle=cmds.ikHandle(sol='ikSplineSolver',
                               createCurve=True,
                               sj=jnts[0],endEffector=jnts[amount])
        
        cmds.setAttr(ikHandle[0]+'.dTwistControlEnable',1)
        cmds.setAttr(ikHandle[0]+'.dWorldUpType',4)
        
        cmds.connectAttr(startMatrix+'.worldMatrix[0]',
                         ikHandle[0]+'.dWorldUpMatrix',force=True)
        cmds.connectAttr(endMatrix+'.worldMatrix[0]',
                         ikHandle[0]+'.dWorldUpMatrixEnd',
                         force=True)
        
        nodes.append(ikHandle[0])
        nodes.append(ikHandle[1])
        nodes.append(ikHandle[2])
        
        #create bend joints
        cmds.select(cl=True)
        pos=cmds.xform(ikHandle[2]+'.cv[1]',q=True,ws=True,
                       translation=True)
        bend01=cmds.joint(p=[0,0,0],n=prefix+'bend01_jnt')
        bend01GRP=cmds.group(bend01,n=prefix+'bend01_grp')
        cmds.xform(bend01GRP,ws=True,translation=pos)        
        mru.Snap(start,bend01GRP,point=False)
        
        nodes.append(bend01)
        nodes.append(bend01GRP)
        
        cmds.select(cl=True)
        pos=cmds.xform(ikHandle[2]+'.cv[2]',q=True,ws=True,
                       translation=True)
        bend02=cmds.joint(p=[0,0,0],n=prefix+'bend02_jnt')
        bend02GRP=cmds.group(bend02,n=prefix+'bend02_grp')
        cmds.xform(bend02GRP,ws=True,translation=pos)        
        mru.Snap(start,bend02GRP,point=False)
        
        nodes.append(bend02)
        nodes.append(bend02GRP)
        
        #setup bend joints
        skin=cmds.skinCluster(start,bend01,bend02,ikHandle[2])[0]
        
        cmds.skinPercent(skin,ikHandle[2]+'.cv[0]',
                         transformValue=[(start, 1)])
        cmds.skinPercent(skin,ikHandle[2]+'.cv[1]',
                         transformValue=[(bend01, 1)])
        cmds.skinPercent(skin,ikHandle[2]+'.cv[2]',
                         transformValue=[(bend02, 1)])
        cmds.skinPercent(skin,ikHandle[2]+'.cv[3]',
                         transformValue=[(start, 1)])
        
        mru.Snap(bendControl,bend01GRP)
        mru.Snap(bendControl,bend02GRP)
        
        cmds.parent(bend01GRP,bendControl)
        cmds.parent(bend02GRP,bendControl)
        
        bend01MD=cmds.shadingNode('multiplyDivide',asUtility=True,
                                  n=prefix+'bend01_md')
        bend02MD=cmds.shadingNode('multiplyDivide',asUtility=True,
                                  n=prefix+'bend02_md')
        bend01PMS=cmds.shadingNode('plusMinusAverage',
                                   asUtility=True,
                                   n=prefix+'bend01_pms')
        
        nodes.append(bend01MD)
        nodes.append(bend02MD)
        nodes.append(bend01PMS)
        
        cmds.setAttr(bend01MD+'.input2X',-dist)
        cmds.setAttr(bend02MD+'.input1Y',dist/1000)
        
        attrs=cmds.attributeInfo(attrControl,all=True)
        
        if 'bendy' not in attrs:
            cmds.addAttr(attrControl,longName='bendy'
                         ,attributeType='float',min=0,max=1,
                         keyable=True,)
        
        cmds.connectAttr(bend02MD+'.outputY',
                         bend01PMS+'.input1D[0]',force=True)
        cmds.connectAttr(attrControl+'.bendy',
                         bend01PMS+'.input1D[1]')
        cmds.connectAttr(bend01PMS+'.output1D',bend01MD+'.input1X')
        cmds.connectAttr(bend01MD+'.outputX',bend01+'.tx')
        cmds.connectAttr(bend01MD+'.outputX',bend02+'.tx')
        
        #making twist joints stretchy
        stretch01MD=cmds.shadingNode('multiplyDivide',
                                     asUtility=True,
                                         n=prefix+'stretch01MD')
        cmds.setAttr(stretch01MD+'.operation',2)
        cmds.setAttr(stretch01MD+'.input2X',dist)
        
        stretch02MD=cmds.shadingNode('multiplyDivide',
                                     asUtility=True,
                                         n=prefix+'stretch02MD')
        cmds.setAttr(stretch02MD+'.operation',2)
        cmds.connectAttr(scaleRoot+'.sx',stretch02MD+'.input2X')
        
        temp=cmds.listRelatives(ikHandle[2],s=True)
        temp1=cmds.arclen(temp[0],ch=True)
        stretchINFO=cmds.rename(temp1,prefix+'stretch_info')
        
        cmds.connectAttr(stretchINFO+'.arcLength',
                         stretch01MD+'.input1X',force=True)
        cmds.connectAttr(stretch01MD+'.outputX',
                         stretch02MD+'.input1X',force=True)
        
        for jnt in jnts:
            cmds.connectAttr(stretch02MD+'.outputX',jnt+'.sx')
        
        #making rig scalable
        cmds.parent(jnts[0],scaleRoot)
        
        #return
        return nodes

'''
templateModule='meta_limb'
Rig(templateModule)
'''