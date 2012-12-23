import maya.cmds as cmds
import maya.mel as mel

from bbt_maya import generic
from bbt_maya.brt import utils
from bbt_maya.brt import twistJoints

class Limb():
    ''' Class for all limb related functions. '''
    
    def Create(self):
        pass
    
    def Import(self):
        pass
    
    def Rig(self,templateModule):
        #class variables
        ut=utils.transform()
        tj=twistJoints.TwistJoints()
        
        #collect all components
        meta=generic.Meta()
        
        controls=meta.downStream(templateModule,'control',
                                 allNodes=True)
        
        for control in controls:
            if meta.getData(control)['component']=='start':
                start=meta.getTransform(control)
            if meta.getData(control)['component']=='mid':
                mid=meta.getTransform(control)
            if meta.getData(control)['component']=='end':
                end=meta.getTransform(control)
        
        #getting transform data
        startTrans=cmds.xform(start,worldSpace=True,query=True,
                              translation=True)
        
        midTrans=cmds.xform(mid,worldSpace=True,query=True,
                            translation=True)
        
        endTrans=cmds.xform(end,worldSpace=True,query=True,
                            translation=True)
        endRot=cmds.xform(end,worldSpace=True,query=True,
                          rotation=True)
        
        #getting asset data
        data=meta.getData(templateModule)
        
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
        data=meta.getData(templateModule)
        
        index=data['index']
        
        for node in cmds.ls(type='network'):
            if meta.getData(node)['type']=='module' and \
            meta.getData(node)['component']==limbType and \
                    meta.getData(node)['side']==side and \
                    meta.getData(node)['index']==index:
                index+=1
        
        #delete template
        cmds.delete(cmds.listConnections('%s.message' % start,
                                         type='dagContainer'))
        
        #establish prefix and suffix
        prefix=side[0]+'_'+limbType+str(index)+'_'
        suffix='_'+side[0]+'_'+limbType+str(index)
        
        #creating asset
        asset=cmds.container(n=prefix+'rig')
        
        #create module
        data={'side':side,'index':str(index)}
        
        module=meta.setData(('meta'+suffix),'module',limbType,None,
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
        
        cmds.xform(plug,worldSpace=True,translation=startTrans)
        
        metaParent=meta.setData('meta_'+plug,'plug',None,module,
                                None)
        
        meta.setTransform(plug, metaParent)
        
        cmds.container(asset,e=True,addNode=plug)
        
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
        metaParent=meta.setData('meta_'+startSocket,'socket',None,
                                module,data)
        meta.setTransform(startSocket, metaParent)
        
        data={'index':2}
        metaParent=meta.setData('meta_'+midSocket,'socket',None,
                                module,data)
        meta.setTransform(midSocket, metaParent)
        
        data={'index':3}
        metaParent=meta.setData('meta_'+endSocket,'socket',None,
                                module,data)
        meta.setTransform(endSocket, metaParent)
        
        cmds.container(asset,e=True,addNode=[startSocket,midSocket,
                                             endSocket])
        
        #finding the worldUpVecter for the joints
        vectorA=[0,0,0]
        vectorB=[0,0,0]
        
        posA=(startTrans[0],startTrans[1],startTrans[2])
        posB=(midTrans[0],midTrans[1],midTrans[2])
        posC=(endTrans[0],endTrans[1],endTrans[2])
        
        vectorA[0]=posA[0]-posB[0]
        vectorA[1]=posA[1]-posB[1]
        vectorA[2]=posA[2]-posB[2]
        
        vectorB[0]=posC[0]-posB[0]
        vectorB[1]=posC[1]-posB[1]
        vectorB[2]=posC[2]-posB[2]
        
        crs=mel.eval('crossProduct <<%s,%s,%s>> <<%s,%s,%s>> 1 1;'\
                        % (vectorA[0],vectorA[1],vectorA[2],
                           vectorB[0],vectorB[1],vectorB[2]))
        
        #setup start joint
        grp=cmds.group(empty=True)
        cmds.xform(grp,worldSpace=True,translation=startTrans)
        cmds.aimConstraint(midJoint,grp,worldUpType='vector',
                           worldUpVector=crs)
        
        rot=cmds.xform(grp,query=True,rotation=True)
        cmds.rotate(rot[0],rot[1],rot[2],startJoint,
                    worldSpace=True,pcp=True)
        
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
        
        diff=ut.closestOrient(midJoint, endJoint)
        
        cmds.rotate(diff[0],diff[1],diff[2],endJoint,r=True,
                    os=True)
        
        #create ik chain
        startIk=cmds.duplicate(startJoint,st=True,po=True,
                               n=prefix+'ik01')[0]
        midIk=cmds.duplicate(midJoint,st=True,po=True,
                             n=prefix+'ik02')[0]
        endIk=cmds.duplicate(endJoint,st=True,po=True,
                             n=prefix+'ik03')[0]
        
        cmds.parent(startIk,plug)
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
        
        cmds.container(asset,e=True,
                       addNode=[stretch01,stretch02,stretchDIST,
                                stretch01MD,stretch02MD,
                                stretchBLD])
        
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
        ucs=utils.controlShape()
        
        polevectorCNT=ucs.sphere(prefix+'polevector_cnt')
        endIkCNT=ucs.sphere(prefix+'endIk_cnt')
        startFkCNT=ucs.box(prefix+'startFk_cnt')
        midFkCNT=ucs.box(prefix+'midFk_cnt')
        endFkCNT=ucs.box(prefix+'endFk_cnt')
        extraCNT=ucs.pin(prefix+'extra_cnt')
        
        cnts=[polevectorCNT,endIkCNT,startFkCNT,midFkCNT,endFkCNT,
              extraCNT]
        
        #setup polevectorCNT
        data={'system':'ik','switch':midFk}
        mNode=meta.setData(('meta_'+polevectorCNT),'control',
                           'polevector', module,data)
        meta.setTransform(polevectorCNT, mNode)
        
        grp=cmds.group(polevectorCNT,n=(polevectorCNT+'_grp'))
        cmds.parent(grp,plug)
        
        phgrp=cmds.group(polevectorCNT,n=(polevectorCNT+'_PH'))
        sngrp=cmds.group(polevectorCNT,n=(polevectorCNT+'_SN'))
        
        ut.snap(polevector,grp)
        
        cmds.parent(polevector,polevectorCNT)
        
        cmds.container(asset,e=True,addNode=[grp,phgrp,sngrp])
        
        #setup endIkCNT
        data={'system':'ik','switch':endFk}
        mNode=meta.setData(('meta_'+endIkCNT),'control','end',
                           module,data)
        
        grp=cmds.group(endIkCNT,n=(endIkCNT+'_grp'))
        cmds.parent(grp,plug)
        
        phgrp=cmds.group(endIkCNT,n=(endIkCNT+'_PH'))
        sngrp=cmds.group(endIkCNT,n=(endIkCNT+'_SN'))
        
        ut.snap(endFk,grp)
        
        cmds.parentConstraint(endIkCNT,stretch02)
        
        cmds.container(asset,e=True,addNode=[grp,phgrp,sngrp])
        
        #setup startFkCNT
        data={'system':'fk','switch':startIk}
        mNode=meta.setData(('meta_'+startFkCNT),'control','start',
                           module,data)
        
        grp=cmds.group(startFkCNT,n=(startFkCNT+'_grp'))
        cmds.parent(grp,plug)
        
        ut.snap(startFk, grp)
        
        cmds.parent(startFk,startFkCNT)
        
        cmds.container(asset,e=True,addNode=grp)
        
        #setup midFkCNT
        data={'system':'fk','switch':midIk}
        mNode=meta.setData(('meta_'+midFkCNT),'control','mid',
                           module,data)
        
        grp=cmds.group(midFkCNT,n=(midFkCNT+'_grp'))
        cmds.parent(grp,startFk)
        
        ut.snap(midFk, grp)
        
        cmds.parent(midFk,midFkCNT)
        
        cmds.container(asset,e=True,addNode=grp)
        
        #setup endFkCNT
        data={'system':'fk','switch':endIkCNT}
        mNode=meta.setData(('meta_'+endFkCNT),'control','end',
                           module,data)
        
        grp=cmds.group(endFkCNT,n=(endFkCNT+'_grp'))
        cmds.parent(grp,midFk)
        
        ut.snap(endFk, grp)
        
        cmds.parent(endFk,endFkCNT)
        
        cmds.container(asset,e=True,addNode=grp)
        
        #setup extraCNT
        mNode=meta.setData(('meta_'+extraCNT),'control','extra',
                           module,None)
        
        cmds.addAttr(extraCNT,ln='FKIK',at='float',keyable=True,
                     min=0,max=1)
        cmds.addAttr(extraCNT,ln='ikTwistControls',at='float',
                     keyable=True,min=0,max=1)
        cmds.addAttr(extraCNT,ln='stretch',at='float',keyable=True,
                     min=0,max=1)
        
        cmds.connectAttr(extraCNT+'.stretch',stretchBLD+'.blender',
                         force=True)
        
        ut.snap(endFk,extraCNT)
        
        cmds.parent(extraCNT,endJoint)
        cmds.rotate(0,90,0,extraCNT,r=True,os=True)
        
        cmds.scaleConstraint(plug,extraCNT)
        
        #create twist controls
        startIkTwistCNT=ucs.circle(prefix+'startIkTwist_cnt')
        midIkTwistCNT=ucs.circle(prefix+'midIkTwist_cnt')
        
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
        mNode=meta.setData(('meta_'+startIkTwistCNT),'control',
                           'iktwist',module,data)
        
        ut.snap(startIk,startIkTwistCNT)
        
        cmds.parent(startIkTwistJNT,startIkTwistCNT)
        cmds.parent(startIkTwistCNT,startIk)
        
        #setup midIkTwistCNT
        data={'system':'ik','switch':midFk,'worldspace':'false',
              'index':2}
        mNode=meta.setData(('meta_'+midIkTwistCNT),'control',
                           'iktwist',module,data)
        
        ut.snap(midIk,midIkTwistCNT)
        
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
        cmds.connectAttr(fkIkREV+'.outputX',midFkCNT+'.visibility')
        cmds.connectAttr(fkIkREV+'.outputX',endFkCNT+'.visibility')
        cmds.connectAttr(extraCNT+'.FKIK',endIkCNT+'.visibility')
        cmds.connectAttr(extraCNT+'.FKIK',polevectorCNT+
                         '.visibility')
        cmds.connectAttr(extraCNT+'.ikTwistControls',
                         startIkTwistCNT+'.visibility')
        cmds.connectAttr(extraCNT+'.ikTwistControls',midIkTwistCNT+
                         '.visibility')
        
        #twist joints        
        if upperTwist==True or lowerTwist==True:
            averageJNT=cmds.joint(p=[0,0,0],n=prefix+'average_jnt')
            
            ut.snap(midFk,averageJNT)
            cmds.parent(averageJNT,midJoint)
            
            orientCon=cmds.orientConstraint(startJoint,midJoint,
                                            averageJNT)
            cmds.setAttr(orientCon[0]+'.interpType',2)
            
            cmds.container(asset,e=True,addNode=[averageJNT])
        
        if upperTwist==True:
            nodes=tj.rig(startJoint,averageJNT,plug,midJoint,
                         averageJNT,extraCNT,plug,upperTwistJoints,
                         prefix+'upper_')
            
            for node in nodes:
                    cmds.container(asset,e=True,
                                   addNode=[node,node])        
            
        if lowerTwist==True:
            nodes=tj.rig(midJoint,endJoint,midJoint,endJoint,
                         averageJNT,extraCNT,plug,lowerTwistJoints,
                         prefix+'lower_')
            
            for node in nodes:
                    cmds.container(asset,e=True,
                                   addNode=[node,node])  
        
        #channelbox cleanup
        attrs=['rx','ry','rz','sx','sy','sz','v']
        ut.channelboxClean(polevectorCNT, attrs)
        
        attrs=['sx','sy','sz','v']
        ut.channelboxClean(endIkCNT, attrs)
        
        attrs=['tx','ty','tz','sx','sy','sz','v']
        ut.channelboxClean(startFkCNT, attrs)
        ut.channelboxClean(midFkCNT, attrs)
        ut.channelboxClean(endFkCNT, attrs)
        
        attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
        ut.channelboxClean(extraCNT, attrs)
        
        attrs=['tx','ty','tz','ry','rz','sx','sy','sz','v']
        ut.channelboxClean(startIkTwistCNT, attrs)
        ut.channelboxClean(midIkTwistCNT, attrs)
        
        #adding controls and publish to asset
        for cnt in cnts:
            cmds.container(asset,e=True,addNode=[cnt])
            cmds.containerPublish(asset,publishNode=(cnt,''))
            cmds.containerPublish(asset,bindNode=(cnt,cnt))

templateModule='meta_limb'

limb=Limb()
limb.Rig(templateModule)
