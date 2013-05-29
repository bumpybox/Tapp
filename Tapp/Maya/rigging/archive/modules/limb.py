import os

import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru
import Tapp.Maya.utils.ZvParentMaster as muz
import MG_Tools.python.script.MG_pathSpine as mpps

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
    jnt01=cmds.joint(name=prefix+'01_jnt')
    cmds.select(cl=True)
    jnt02=cmds.joint(name=prefix+'02_jnt')
    cmds.select(cl=True)
    jnt03=cmds.joint(name=prefix+'03_jnt')
    
    cmds.container(asset,e=True,addNode=[jnt01,jnt02,
                                         jnt03])
    
    #setup jnts
    cmds.xform(jnt01,ws=True,translation=startTrans)
    cmds.xform(jnt02,ws=True,translation=midTrans)
    cmds.xform(jnt03,ws=True,translation=endTrans)
    
    #finding the upVector for the joints
    crs=mru.CrossProduct(startTrans,midTrans,endTrans)
    
    #setup start joint
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=startTrans)
    cmds.aimConstraint(jnt02,grp,worldUpType='vector',
                       worldUpVector=crs)
    
    rot=cmds.xform(grp,query=True,rotation=True)
    cmds.rotate(rot[0],rot[1],rot[2],jnt01,
                worldSpace=True,pcp=True)
    
    mru.Snap(jnt01, plug)
    
    cmds.makeIdentity(jnt01,apply=True,t=1,r=1,s=1,n=0)
    
    cmds.delete(grp)
    
    #setup mid and end joint
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=midTrans)
    cmds.aimConstraint(jnt03,grp,worldUpType='vector',
                       worldUpVector=crs)
    
    rot=cmds.xform(grp,query=True,rotation=True)
    cmds.rotate(rot[0],rot[1],rot[2],jnt02,worldSpace=True,
                pcp=True)
    
    cmds.delete(grp)
    
    cmds.rotate(rot[0],rot[1],rot[2],jnt03,worldSpace=True,
                pcp=True)
    
    cmds.makeIdentity(jnt02,apply=True, t=1, r=1, s=1, n=0)
    cmds.makeIdentity(jnt03,apply=True, t=1, r=1, s=1, n=0)
    
    #setup end joint
    cmds.xform(jnt03,worldSpace=True,rotation=endRot)
    
    mru.ClosestOrient(jnt02, jnt03)
    
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
    
    cmds.parent(startSocket,jnt01)
    cmds.parent(midSocket,jnt02)
    cmds.parent(endSocket,jnt03)
    
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
        fk01cnt=mru.Box(prefix+'startFk_cnt')
        fk02cnt=mru.Box(prefix+'midFk_cnt')
        fk03cnt=mru.Box(prefix+'endFk_cnt')
        
        cmds.container(asset,e=True,addNode=[fk01cnt,fk02cnt,fk03cnt])
        
        #setup fk01cnt
        data={'system':'fk','index':1}
        mNode=mum.SetData(('meta_'+fk01cnt),'control','start',
                           module,data)
        mum.SetTransform(fk01cnt, mNode)
        
        grp=cmds.group(fk01cnt,n=(fk01cnt+'_grp'))
        
        cmds.container(asset,e=True,addNode=grp)
        
        cmds.parent(grp,plug)
        
        mru.Snap(jnt01, grp)
        
        #setup fk02cnt
        data={'system':'fk','index':2}
        mNode=mum.SetData(('meta_'+fk02cnt),'control','mid',
                           module,data)
        mum.SetTransform(fk02cnt,mNode)
        
        grp=cmds.group(fk02cnt,n=(fk02cnt+'_grp'))
        cmds.container(asset,e=True,addNode=grp)
        
        cmds.parent(grp,fk01cnt)
        
        mru.Snap(jnt02, grp)
        
        #setup fk03cnt
        data={'system':'fk','index':3}
        mNode=mum.SetData(('meta_'+fk03cnt),'control','end',
                           module,data)
        mum.SetTransform(fk03cnt,mNode)
        
        grp=cmds.group(fk03cnt,n=(fk03cnt+'_grp'))
        cmds.container(asset,e=True,addNode=grp)
        
        cmds.parent(grp,fk02cnt)
        
        mru.Snap(jnt03, grp)
        
        cmds.xform(grp,ws=True,rotation=endRot)
        
        #channelbox clean
        cnts=[fk01cnt,fk02cnt,fk03cnt]
        
        attrs=['sx','sy','sz']
        for cnt in cnts:
            mru.ChannelboxClean(cnt,attrs)
    
    #create ik---
    if ik:
        cmds.select(cl=True)
        ik01jnt=cmds.joint(n=prefix+'ik01')
        ik02jnt=cmds.joint(n=prefix+'ik02')
        ik03jnt=cmds.joint(n=prefix+'ik03')
        
        cmds.container(asset,e=True,addNode=[ik01jnt,ik02jnt,ik03jnt])
        
        #setup ik
        cmds.parent(ik01jnt,plug)
        cmds.parent(ik02jnt,ik01jnt)
        cmds.parent(ik03jnt,ik02jnt)
        
        mru.Snap(jnt01,ik01jnt)
        mru.Snap(jnt02,ik02jnt)
        mru.Snap(jnt03,ik03jnt)
        
        cmds.makeIdentity(ik01jnt,apply=True,t=1,r=1,s=1,n=0)
        cmds.makeIdentity(ik02jnt,apply=True,t=1,r=1,s=1,n=0)
        cmds.makeIdentity(ik03jnt,apply=True,t=1,r=1,s=1,n=0)
        
        #create ik handle
        ikHandle=cmds.ikHandle(sj=ik01jnt,ee=ik03jnt,sol='ikRPsolver',
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
        
        mru.Snap(jnt03,phgrp)
        mru.Snap(jnt03,stretch02)
        cmds.parentConstraint(stretch02REF,stretch02)
        
        cmds.scaleConstraint(plug,phgrp)
        
        cmds.transformLimits(ik01jnt,sx=(1,1),esx=(1,0))
        cmds.transformLimits(ik02jnt,sx=(1,1),esx=(1,0))
        
        temp1=mru.Distance(jnt01, jnt02)
        temp2=mru.Distance(jnt02,jnt03)
        
        cmds.setAttr('%s.color2R' % stretchBLD,1)
        cmds.setAttr('%s.blender' % stretchBLD,1)
        cmds.setAttr('%s.input2X' % stretch02MD,temp1+temp2)
        cmds.setAttr('%s.operation' % stretch01MD,2)
        
        cmds.pointConstraint(ik01jnt,stretch01)
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
                         '%s.sx' % ik01jnt,force=True)
        cmds.connectAttr('%s.outputR' % stretchBLD,
                         '%s.sx' % ik02jnt,force=True)
        
        #create controls
        ikpolevectorcnt=mru.Sphere(prefix+'polevector_cnt')
        ikendcnt=mru.Sphere(prefix+'end_cnt')
        
        cmds.container(asset,e=True,addNode=[ikpolevectorcnt,ikendcnt])
        
        #setup ikpolevectorcnt
        data={'system':'ik','index':2}
        mNode=mum.SetData(('meta_'+ikpolevectorcnt),'control',
                           'polevector', module,data)
        mum.SetTransform(ikpolevectorcnt, mNode)
        
        cmds.xform(ikpolevectorcnt,worldSpace=True,translation=midTrans)
        
        rot=cmds.xform(jnt02,worldSpace=True,q=True,
                       rotation=True)
        cmds.xform(ikpolevectorcnt,worldSpace=True,rotation=rot)
        
        tx=mru.Distance(jnt01,jnt02)+mru.Distance(jnt02, jnt03)
        cmds.move(0,0,-tx/3,ikpolevectorcnt,r=True,os=True,wd=True)
        
        phgrp=cmds.group(empty=True,n=(ikpolevectorcnt+'_PH'))
        sngrp=cmds.group(empty=True,n=(ikpolevectorcnt+'_SN'))
        
        cmds.container(asset,e=True,addNode=[phgrp,sngrp])
        
        cmds.delete(cmds.parentConstraint(ikpolevectorcnt,phgrp))
        cmds.delete(cmds.parentConstraint(ikpolevectorcnt,sngrp))
        
        cmds.parent(ikpolevectorcnt,sngrp)
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
        
        mru.Snap(ikpolevectorcnt,cluster[1])
        cmds.parent(cluster[1],ikpolevectorcnt)
        
        cmds.rename(cluster[0],prefix+'polvector_cls')
        
        cmds.select(curve+'.cv[1]',r=True)
        cluster=mel.eval('newCluster " -envelope 1";')
        
        cmds.container(asset,e=True,addNode=[cluster[0],
                                             cluster[1]])
        
        mru.Snap(ik02jnt,cluster[1])
        cmds.parent(cluster[1],ik02jnt)
        
        cmds.rename(cluster[0],prefix+'polvector_cls')
        polevectorSHP=cmds.rename(curve,prefix+'polevector_shp')
        
        cmds.poleVectorConstraint(ikpolevectorcnt,ikHandle[0])
        
        #setup ikendcnt
        data={'system':'ik','index':1}
        mNode=mum.SetData(('meta_'+ikendcnt),'control','end',
                           module,data)
        mum.SetTransform(ikendcnt, mNode)
        
        grp=cmds.group(empty=True,n=(ikendcnt+'_grp'))
        phgrp=cmds.group(empty=True,n=(ikendcnt+'_PH'))
        sngrp=cmds.group(empty=True,n=(ikendcnt+'_SN'))
        
        cmds.container(asset,e=True,addNode=[grp,phgrp,sngrp])
        
        cmds.parent(grp,plug)
        cmds.parent(phgrp,grp)
        cmds.parent(sngrp,phgrp)
        cmds.parent(ikendcnt,sngrp)
        
        mru.Snap(jnt03,grp)
        
        cmds.select([stretch02REF,ikendcnt],r=True)
        muz.attach()
        
        cmds.xform(phgrp,ws=True,rotation=endRot)
        
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
        
        mru.Snap(ik01jnt,ik01cnt)
        
        cmds.parent(ik01cnt,ik01jnt)
        
        #setup ik02cnt
        data={'system':'ik','worldspace':'false',
              'index':4}
        mNode=mum.SetData(('meta_'+ik02cnt),'control',
                           'iktwist',module,data)
        mum.SetTransform(ik02cnt,mNode)
        
        mru.Snap(ik02jnt,ik02cnt)
        
        cmds.parent(ik02cnt,ik02jnt)
        
        #setup ik03cnt
        data={'system':'ik','worldspace':'false',
              'index':5}
        mNode=mum.SetData(('meta_'+ik03cnt),'control',
                           'iktwist',module,data)
        mum.SetTransform(ik03cnt,mNode)
        
        mru.Snap(ik03jnt,ik03cnt)
        
        cmds.parent(ik03cnt,ikendcnt)
        
        cmds.xform(ik03cnt,ws=True,rotation=endRot)
        
        #channelbox clean
        cnts=[ikpolevectorcnt,ikendcnt,ik01cnt,ik02cnt,ik03cnt]
        
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
        
        mru.Snap(jnt03,extraCNT)
        
        cmds.parent(extraCNT,jnt03)
        cmds.rotate(0,90,0,extraCNT,r=True,os=True)
        
        cmds.scaleConstraint(plug,extraCNT)
        
        #setup blending
        fkIkREV=cmds.shadingNode('reverse',asUtility=True,
                                 n=(prefix+'fkIkREV'))
        
        cmds.container(asset,e=True,addNode=[fkIkREV])
        
        cmds.connectAttr(extraCNT+'.FKIK',fkIkREV+'.inputX')
        
        con=cmds.parentConstraint(ik01cnt,fk01cnt,jnt01)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+
                         fk01cnt+'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+
                         ik01cnt+'W0',force=True)
        
        con=cmds.parentConstraint(ik02cnt,fk02cnt,jnt02)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+fk02cnt+
                         'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+
                         ik02cnt+'W0',force=True)
        
        con=cmds.orientConstraint(ik03cnt,fk03cnt,jnt03)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+fk03cnt+
                         'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+
                         ik03cnt+'W0',force=True)
        
        con=cmds.pointConstraint(ik03jnt,fk03cnt,jnt03)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+fk03cnt+
                         'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+
                         ik03jnt+'W0',force=True)
        
        con=cmds.scaleConstraint(ik01cnt,fk01cnt,jnt01)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+
                         fk01cnt+'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+ik01cnt+
                         'W0',force=True)
        
        con=cmds.scaleConstraint(ik02cnt,fk02cnt,jnt02)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+
                         fk02cnt+'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+ik02cnt+
                         'W0',force=True)
        
        con=cmds.scaleConstraint(ik03cnt,fk03cnt,jnt03)
        cmds.connectAttr(fkIkREV+'.outputX',con[0]+'.'+
                         fk03cnt+'W1',force=True)
        cmds.connectAttr(extraCNT+'.FKIK',con[0]+'.'+ik03cnt+
                         'W0',force=True)
        
        cmds.connectAttr(fkIkREV+'.outputX',fk01cnt+'.visibility')
        cmds.connectAttr(fkIkREV+'.outputX',fk02cnt+'.v')
        cmds.connectAttr(fkIkREV+'.outputX',fk03cnt+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',ikendcnt+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',ikpolevectorcnt+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',polevectorSHP+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',ik01cnt+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',ik02cnt+'.v')
        cmds.connectAttr(extraCNT+'.FKIK',ik03cnt+'.v')
        
        #setup switching
        data={'switch':ik01cnt}
        mum.ModifyData(fk01cnt, data)
        
        data={'switch':ik02cnt}
        mum.ModifyData(fk02cnt, data)
        
        data={'switch':ik03cnt}
        mum.ModifyData(fk03cnt, data)
        
        data={'switch':fk01cnt}
        mum.ModifyData(ik01cnt, data)
        
        data={'switch':fk02cnt}
        mum.ModifyData(ik02cnt, data)
        
        data={'switch':fk03cnt}
        mum.ModifyData(ik03cnt, data)
        
        data={'switch':fk03cnt}
        mum.ModifyData(ikendcnt, data)
        
        data={'switch':fk02cnt}
        mum.ModifyData(ikpolevectorcnt, data)
        
        #channelbox clean
        attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
        mru.ChannelboxClean(extraCNT,attrs)
    
    #twist joints---
    tj=TwistJoints()
    if upperTwist=='True' or lowerTwist=='True':
        
        averageJNT=cmds.joint(p=[0,0,0],n=prefix+'average_jnt')
        
        cmds.container(asset,e=True,addNode=averageJNT)
        
        mru.Snap(jnt02,averageJNT)
        cmds.parent(averageJNT,jnt02)
        
        orientCon=cmds.orientConstraint(jnt01,jnt02,
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
        result=tj.Rig(jnt01, jnt02, prefix+'upper_', int(upperTwistJoints),
                      asset, plug)
        
        cmds.parent(result['upvectors'][0],plug)
        cmds.parent(result['joints'][3],averageJNT)
        
        cmds.parentConstraint(jnt02,result['twistend'],mo=True)
        
        for loc in result['locators']:
            
            meta=mum.SetData('meta_'+loc, 'joint', None, module, None)
            mum.SetTransform(loc, meta)
        
        #bend amount
        cmds.scale(0.001,0.001,0.001,result['joints'][0])
        
        mru.Snap(jnt02,result['joints'][3])
        mru.Snap(jnt02,result['joints'][2])
        mru.Snap(jnt01,result['joints'][3],point=False)
        
        
        dist=mru.Distance(jnt01,jnt02)
        
        cmds.move(-dist/2,0,0,result['joints'][2],os=True)
        
        cmds.connectAttr(extraCNT+'.bendAmount',result['joints'][3]+'.sx')
        cmds.connectAttr(extraCNT+'.bendAmount',result['joints'][3]+'.sy')
        cmds.connectAttr(extraCNT+'.bendAmount',result['joints'][3]+'.sz')
        
        #bend control
        con=cmds.orientConstraint(averageJNT,jnt01,result['joints'][3])
        
        cmds.setAttr(con[0]+'.interpType',2)
        
        cmds.connectAttr(bendRev+'.outputX',con[0]+'.'+jnt01+
                         'W1',force=True)
        
        cmds.connectAttr(extraCNT+'.bend',con[0]+'.'+
                         averageJNT+'W0',force=True)
        
    else:
        meta=mum.SetData('meta_'+jnt01, 'joint', None, module, None)
        mum.SetTransform(jnt01, meta)
        
    if lowerTwist=='True':
        result=tj.Rig(jnt02,jnt03,prefix+'lower_', int(lowerTwistJoints),
                      asset, plug)
        
        cmds.parent(result['upvectors'][0],jnt01)
        cmds.parent(result['twiststartgrp'],jnt01)
        cmds.parent(result['twistendgrp'],jnt01)
        
        cmds.parentConstraint(jnt02,result['twiststart'],mo=True)
        cmds.parentConstraint(jnt03,result['twistend'],mo=True)
        
        cmds.move(0,0,-1,result['upvectors'][1],os=True)
        
        for loc in result['locators']:
            
            meta=mum.SetData('meta_'+loc, 'joint', None, module, None)
            mum.SetTransform(loc, meta)
        
        #bend Amount
        cmds.scale(0,0,0,result['joints'][3])
        
        mru.Snap(jnt02,result['joints'][0])
        mru.Snap(jnt02,result['joints'][1])
        
        dist=mru.Distance(jnt01,jnt02)
        
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
        con=cmds.orientConstraint(averageJNT,jnt02,result['joints'][0])
        
        cmds.setAttr(con[0]+'.interpType',2)
        
        cmds.connectAttr(bendRev+'.outputX',con[0]+'.'+jnt02+
                         'W1',force=True)
        
        cmds.connectAttr(extraCNT+'.bend',con[0]+'.'+
                         averageJNT+'W0',force=True)
        
    else:
        meta=mum.SetData('meta_'+jnt02, 'joint', None, module, None) 
        mum.SetTransform(jnt02, meta)
        
    meta=mum.SetData('meta_'+jnt03, 'joint', None, module, None) 
    mum.SetTransform(jnt03, meta)

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
        
        cmds.setAttr(curve+'.v',0)
        
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