import os

import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru

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
    
    jntsTrans=[]
    
    grp=cmds.group(empty=True)
    path=cmds.pathAnimation(grp,follow=True,c=line)
    
    for count in xrange(0,jointAmount+1):
        pct=1.0/jointAmount*count
        
        cmds.setAttr(path+'.uValue',pct)
        
        trans=cmds.xform(grp,q=True,ws=True,translation=True)
        jntsTrans.append(trans)
    
    cmds.delete(grp,path)
    
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
    asset=cmds.container(n=prefix+'rig')
    
    #create module
    data={'side':side,'index':str(index),'system':'rig','subcomponent':spineType}
    
    module=mum.SetData(('meta'+suffix),'module','spine',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #create plug
    plug=cmds.spaceLocator(name=prefix+'plug')[0]
    
    phgrp=cmds.group(plug,n=(plug+'_PH'))
    sngrp=cmds.group(plug,n=(plug+'_SN'))
    
    cmds.xform(phgrp,worldSpace=True,translation=startTrans)
    
    metaParent=mum.SetData('meta_'+plug,'plug',None,module,
                            None)
    
    mum.SetTransform(plug, metaParent)
    
    cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
    
    #create fkjnts, ikjnts, jnts, sockets, fkcnts, ikcnts
    ikcnts=[]
    ikcntsGRP=[]
    fkcnts=[]
    fkcntsGRP=[]
    fkjnts=[]
    ikjnts=[]
    jnts=[]
    sockets=[]
    iktwistcnts=[]
    ikfinecnts=[]
    
    for pos in jntsTrans:
        
        count=jntsTrans.index(pos)+1
        
        #create joints
        jnt=cmds.joint(position=(pos[0],pos[1],pos[2]),
                              name=prefix+'jnt'+str(count))
        
        cmds.container(asset,e=True,addNode=jnt)
        
        meta=mum.SetData('meta_'+jnt, 'joint', None, module, None)
        mum.SetTransform(jnt, meta)
        
        if len(jnts)>0:
            cmds.parent(jnt,jnts[-1])
            
            try:
                cmds.connectAttr(jnts[-1]+'.scale',
                                 jnt+'.inverseScale')
            except:
                pass
        
        jnts.append(jnt)
        
        if len(jnts)<jointAmount+1:
            grp=cmds.group(empty=True)
            newPos=jntsTrans[count]
            cmds.xform(grp,worldSpace=True,
                       translation=newPos)
            aimCon=cmds.aimConstraint(grp,jnt,
                                      worldUpVector=(1,0,0))
            cmds.delete(aimCon)
            
            cmds.makeIdentity(jnt,apply=True,t=1,r=1,s=1,n=0)
            
            cmds.delete(grp)
        else:
            mru.Snap(jnts[-2],jnt,point=False)
        
        #create sockets
        socket=cmds.spaceLocator(name=prefix+'socket'+
                                 str(count))[0]
        
        mru.Snap(jnt,socket)
        cmds.parent(socket,jnt)
        
        data={'index':count}
        metaParent=mum.SetData('meta_'+socket,'socket',None,
                                module,data)
        mum.SetTransform(socket, metaParent)
        
        sockets.append(socket)
        
        cmds.container(asset,e=True,addNode=socket)
        
        #create fk
        cmds.select(cl=True)
        fk=cmds.joint(position=(pos[0],pos[1],pos[2]),
                              name=prefix+'fk'+str(count))
        
        mru.Snap(jnt,fk)
        cmds.makeIdentity(fk,apply=True,t=1,r=1,s=1,n=0)
        
        cmds.container(asset,e=True,addNode=fk)
        
        #create fk controls
        [grp,cnt]=mru.Square(prefix+'fk'+str(count)+'_cnt',
                       group=True)
        
        cmds.container(asset,e=True,addNode=[grp,cnt])
        
        fkcnts.append(cnt)
        fkcntsGRP.append(grp)
        
        #create ik
        cmds.select(cl=True)
        ik=cmds.joint(position=(pos[0],pos[1],pos[2]),
                              name=prefix+'ik'+str(count))
        
        mru.Snap(jnt,ik)
        cmds.makeIdentity(ik,apply=True,t=1,r=1,s=1,n=0)
        
        cmds.container(asset,e=True,addNode=ik)
        
        #setup fk controls
        mru.Snap(fk,grp)
        
        cmds.parent(fk,cnt)
        
        if len(fkjnts)>0:
            cmds.parent(grp,fkjnts[-1])
        
        fkjnts.append(fk)
        
        data={'system':'fk','switch':ik,'index':count}
        mNode=mum.SetData(('meta_'+cnt),'control',
                           'joint',module,data)
        mum.SetTransform(cnt, mNode)
        
        #setup ik jnts
        if count<jointAmount+1:
            if len(ikjnts)>0:
                cmds.parent(ik,ikjnts[-1])
            
            ikjnts.append(ik)
        else:
            cmds.parent(ik,ikjnts[-1])
            
            ikjnts.append(ik)
        
        #create ik controls
        if count<=jointAmount and count>1:
            [grp,cnt]=mru.Sphere(prefix+'ik'+str(count-1)+'_cnt',
                           group=True)
            
            cmds.container(asset,e=True,addNode=[grp,cnt])
            
            ikcnts.append(cnt)
            ikcntsGRP.append(grp)
            ikfinecnts.append(cnt)
            
            #setup ik controls
            mru.Snap(ik,grp)
            
            data={'system':'ik','switch':fk,'index':count+3}
            mNode=mum.SetData(('meta_'+cnt),'control',
                               'joint',module,data)
            mum.SetTransform(cnt, mNode)
        
        #create ik twist controls
        if count<=jointAmount and count>1:
            [grp,cnt]=mru.Circle(prefix+'ikTwist'+str(count-1)+'_cnt',
                           group=True)
            
            cmds.container(asset,e=True,addNode=[grp,cnt])
            
            iktwistcnts.append(cnt)
            
            #setup ik controls
            mru.Snap(ik,grp)
            
            data={'system':'ik','switch':fk,'index':count+3+(jointAmount-1)}
            mNode=mum.SetData(('meta_'+cnt),'control',
                               'joint',module,data)
            mum.SetTransform(cnt, mNode)
    
    cmds.parent(jnts[0],plug)
    cmds.parent(fkcntsGRP[0],plug)
    
    #create end fk joint
    endFk=cmds.joint(position=(0,0,0),n=prefix+'fk_end')
    
    cmds.container(asset,e=True,addNode=endFk)
    
    #setup end fk joint
    cmds.xform(endFk,ws=True,translation=endTrans)
    cmds.xform(endFk,ws=True,rotation=endRot)
    
    mru.ClosestOrient(fkjnts[-1], endFk)
    
    cmds.parent(endFk,fkjnts[-1])
    
    #create controls
    ikhighcnts=[]
    
    [endGRP,endCNT]=mru.Sphere(prefix+'end_cnt',group=True)
    [midGRP,midCNT]=mru.Sphere(prefix+'mid_cnt',group=True)
    
    cnts=[endCNT,midCNT]
    cntsGRP=[endGRP,midGRP]
    
    cmds.container(asset,e=True,addNode=cnts)
    cmds.container(asset,e=True,addNode=cntsGRP)
    
    ikhighcnts.append(endCNT)
    ikhighcnts.append(midCNT)
    
    #create master control
    if spineType=='spine':
        [masterGRP,masterCNT]=mru.FourWay(prefix+'master_cnt',
                                        group=True)
        
        cmds.container(asset,e=True,addNode=[masterGRP,masterCNT])
        
        #setup master control
        cmds.xform(masterGRP,ws=True,translation=startTrans)
        cmds.xform(masterGRP,ws=True,rotation=startRot)
        
        mru.ClosestOrient(jnts[0], masterGRP, align=True)
        
        cmds.parent(masterGRP,plug)
        cmds.parent(fkcntsGRP[0],masterCNT)
        
        mNode=mum.SetData(('meta_'+masterCNT),'control',
                           'master',module,None)
        mum.SetTransform(masterCNT, mNode)
    
    #create start joint
    cmds.select(cl=True)
    startJNT=cmds.joint(n=prefix+'start_jnt')
    
    cmds.container(asset,e=True,addNode=startJNT)
    
    #setup start joint
    cmds.xform(startJNT,ws=True,translation=startTrans)
    cmds.xform(startJNT,ws=True,rotation=startRot)
    
    mru.ClosestOrient(jnts[0],startJNT, align=True)
    
    cmds.parent(startJNT,plug)
    
    #setup end control
    cmds.xform(endGRP,ws=True,translation=endTrans)
    cmds.xform(endGRP,ws=True,rotation=endRot)
    
    mru.ClosestOrient(jnts[0],endGRP, align=True)
    
    if spineType=='spine':
        cmds.parent(endGRP,masterCNT)
    else:
        cmds.parent(endGRP,plug)
    
    cmds.select(cl=True)
    endJNT=cmds.joint(n=prefix+'end_jnt')
    
    cmds.container(asset,e=True,addNode=endJNT)
    
    mru.Snap(endCNT,endJNT)
    cmds.parent(endJNT,endCNT)
    
    data={'system':'ik','switch':fkcnts[-1],'index':1}
    mNode=mum.SetData(('meta_'+endCNT),'control',
                       'end',module,data)
    mum.SetTransform(endCNT, mNode)
    
    ikcnts.append(endCNT)
    
    data={'switch':endJNT}
    mum.ModifyData(fkcnts[-1], data)
    
    #setup mid control
    cmds.delete(cmds.parentConstraint(startJNT,endJNT,midGRP))
    
    midposGRP=cmds.group(empty=True,n=prefix+'midPos_grp')
    midaimatGRP=cmds.group(empty=True,n=prefix+'midAimAt_grp')
    midaimupGRP=cmds.group(empty=True,n=prefix+'midAimUp_grp')
    
    cmds.container(asset,e=True,addNode=[midposGRP,
                                         midaimatGRP,
                                         midaimupGRP])
    
    mru.Snap(midGRP,midposGRP)
    mru.Snap(midGRP,midaimatGRP)
    mru.Snap(midGRP,midaimupGRP)
    
    cmds.move(spineLength/10.0,0,0,midaimatGRP,r=True,os=True)
    cmds.move(0,spineLength/10.0,0,midaimupGRP,r=True,os=True)
    
    cmds.pointConstraint(midposGRP,midGRP)
    cmds.aimConstraint(midaimatGRP,midGRP,aimVector=[1,0,0],
                       upVector=[0,1,0],worldUpType='object',
                       worldUpObject=midaimupGRP)
    cmds.parentConstraint(startJNT,endJNT,midposGRP,
                          maintainOffset=True)
    cmds.parentConstraint(startJNT,endJNT,midaimatGRP,
                          maintainOffset=True)
    cmds.parentConstraint(startJNT,endJNT,midaimupGRP,
                          maintainOffset=True)
    
    cmds.scaleConstraint(plug,midGRP)
    
    cmds.select(cl=True)
    midJNT=cmds.joint(n=prefix+'mid_jnt')
    
    cmds.container(asset,e=True,addNode=midJNT)
    
    mru.Snap(midCNT,midJNT)
    cmds.parent(midJNT,midCNT)
    
    zeroGRP=cmds.group(empty=True,n=prefix+'zero_grp')
    
    cmds.container(asset,e=True,addNode=zeroGRP)
    
    mru.Snap(midGRP,zeroGRP)
    cmds.parent(zeroGRP,midGRP)
    
    data={'system':'ik','switch':zeroGRP,'index':2}
    mNode=mum.SetData(('meta_'+midCNT),'control',
                       'mid',module,data)
    mum.SetTransform(midCNT, mNode)
    
    ikcnts.append(midCNT)
    
    #create start control
    if spineType=='spine':
        [startGRP,startCNT]=mru.Sphere(prefix+'start_cnt',
                                       group=True)
        
        cmds.container(asset,e=True,addNode=startCNT)
        
        #setup start control
        mru.ClosestOrient(jnts[0], startGRP, align=True)
        
        cmds.parent(startGRP,masterCNT)
        
        mru.Snap(startJNT,startGRP)
        cmds.parent(startJNT,startCNT)
        
        data={'system':'ik','switch':fkcnts[0],'index':3}
        mNode=mum.SetData(('meta_'+startCNT),'control',
                           'start',module,data)
        mum.SetTransform(startCNT, mNode)
        
        ikcnts.append(startCNT)
        ikhighcnts.append(startCNT)
    
    #create spine geo
    spineGEO=cmds.nurbsPlane(p=[0,0,0],ax=[0,1,0],
                             w=spineLength/3,
                             lr=spineLength/(spineLength/3),
                             d=3,u=1,v=2,ch=True,
                             n=prefix+'geo')[0]
    
    cmds.container(asset,e=True,addNode=spineGEO)
    
    #setup spine geo
    mru.Snap(midCNT,spineGEO)
    
    temp=cmds.group(empty=True)
    mru.Snap(midCNT,temp)
    cmds.move(0,0,spineLength,temp,os=True,r=True)
    
    cmds.delete(cmds.aimConstraint(endCNT,spineGEO,
                                   aimVector=[0,0,-1],
                                   upVector=[0,1,0],
                                   worldUpType='object',
                                   worldUpObject=temp))
    
    cmds.delete(temp)
    
    cmds.rebuildSurface(spineGEO,ch=True,rpo=True,rt=False,
                        end=True,kr=False,kcp=False,kc=False,
                        su=True,du=True,sv=5,dv=True,tol=0.01,
                        fr=False,dir=False)
    
    cmds.select(spineGEO,r=True)
    cmds.DeleteHistory()
    cmds.select(cl=True)
    
    skin=cmds.skinCluster(startJNT,midJNT,endJNT,spineGEO,
                          tsb=True)
    
    cmds.skinPercent(skin[0],spineGEO+'.cv[0:1][0]',
                     tv=[(startJNT,1.0)])
    cmds.skinPercent(skin[0],spineGEO+'.cv[0:1][1]',
                     tv=[(startJNT,1.0)])
    cmds.skinPercent(skin[0],spineGEO+'.cv[0:1][3]',
                     tv=[(endJNT,1.0)])
    cmds.skinPercent(skin[0],spineGEO+'.cv[0:1][4]',
                     tv=[(endJNT,1.0)])
    cmds.skinPercent(skin[0],spineGEO+'.cv[0:1][2]',
                     tv=[(midJNT,1.0)])
    cmds.skinPercent(skin[0],spineGEO+'.cv[0:1][1]',
                     tv=[(midJNT,0.333)])
    cmds.skinPercent(skin[0],spineGEO+'.cv[0:1][3]',
                     tv=[(midJNT,0.333)])
    
    cmds.setAttr(spineGEO+'.v',False)
    
    #setup ik jnts
    cmds.parent(ikjnts[0],startJNT)
    
    posgrps=[startJNT]
    
    for jnt in ikjnts:
        count=ikjnts.index(jnt)+1
        
        if count<jointAmount+1:
            #create surface grps
            posGRP=cmds.group(empty=True,
                              n=prefix+'pos'+str(count)+'_grp')
            upGRP=cmds.group(empty=True,
                             n=prefix+'up'+str(count)+'_grp')
            psi=cmds.createNode('pointOnSurfaceInfo',
                                n=prefix+str(count)+'_psi')
            
            cmds.container(asset,e=True,addNode=[posGRP,upGRP,
                                                 psi])
            
            posgrps.append(posGRP)
            
            #setup surface grps
            cmds.parent(upGRP,posGRP)
            
            cmds.setAttr(psi+'.parameterU',0.5)
            cmds.setAttr(psi+'.parameterV',
                         (1.0/jointAmount)*count)
            
            cmds.connectAttr(spineGEO+'.worldSpace',
                             psi+'.inputSurface')
            cmds.connectAttr(psi+'.position',
                             posGRP+'.translate')
            cmds.connectAttr(psi+'.tangentU',
                             upGRP+'.translate')
            
            #create ik handle
            ikHandle=cmds.ikHandle(sj=jnt,ee=ikjnts[count],
                                   sol='ikRPsolver')
            
            cmds.container(asset,e=True,addNode=ikHandle)
            
            #setup ik handle
            if count<jointAmount:
                cmds.parent(ikcntsGRP[count-1],posgrps[count])
                
                cmds.parent(iktwistcnts[count-1],ikjnts[count])
            
            cmds.parent(ikHandle[0],ikcnts[count-1])
            
            cmds.poleVectorConstraint(upGRP,ikHandle[0])
            
            cmds.setAttr(ikHandle[0]+'.twist',-90)
    
    #create extra control
    extraCNT=mru.Pin(prefix+'extra_cnt')
    
    mNode=mum.SetData(('meta_'+extraCNT),'control',
                       'extra',module,None)
    mum.SetTransform(extraCNT, mNode)
    
    cmds.container(asset,e=True,addNode=extraCNT)
    
    #setup extra control
    mru.Snap(endCNT,extraCNT)
    
    cmds.parent(extraCNT,jnts[-1])
    
    cmds.setAttr(extraCNT+'.ry',-90)
    
    #setup fine tune controls
    cmds.addAttr(extraCNT,ln='ikFineTune',at='float',
                 keyable=True,min=0,max=1)
    
    for cnt in iktwistcnts:
        cmds.connectAttr(extraCNT+'.ikFineTune',
                         cnt+'.v')
    
    for cnt in ikfinecnts:
        cmds.connectAttr(extraCNT+'.ikFineTune',
                         cnt+'.v')
    
    #setup stretching
    cmds.addAttr(extraCNT,ln='squashStretch',at='float',
                 keyable=True,min=0,max=1)
    cmds.addAttr(plug,ln='squashStretch',at='float')
    cmds.setKeyframe(plug,at='squashStretch',t=0,v=0)
    cmds.setKeyframe(plug,at='squashStretch',t=jointAmount+1,
                     v=0)
    cmds.setKeyframe(plug,at='squashStretch',
                     t=(jointAmount+1)/2.0,
                     v=1)
    cmds.keyTangent(plug,at='squashStretch',wt=1)
    cmds.keyTangent(plug,at='squashStretch',weightLock=False)
    
    ikblend=[]
    iksquash=[]
    
    for ik in ikjnts:
        count=ikjnts.index(ik)+1
        
        if count<=jointAmount:
            dist=cmds.shadingNode('distanceBetween',
                                  n=prefix+'stretch_dist',
                                  asUtility=True)
            blend=cmds.shadingNode('blendColors',
                                   n=prefix+'stretch_blend',
                                   asUtility=True)
            fc=cmds.shadingNode('frameCache',
                                n=prefix+'stretch_fc',
                                asUtility=True)
            md01=cmds.shadingNode('multiplyDivide',
                                n=prefix+'stretch_md',
                                asUtility=True)
            md02=cmds.shadingNode('multiplyDivide',
                                n=prefix+'stretch_md',
                                asUtility=True)
            md03=cmds.shadingNode('multiplyDivide',
                                n=prefix+'stretch_md',
                                asUtility=True)
            md04=cmds.shadingNode('multiplyDivide',
                                n=prefix+'stretch_md',
                                asUtility=True)
            md05=cmds.shadingNode('multiplyDivide',
                                n=prefix+'stretch_md',
                                asUtility=True)
            
            ikblend.append(blend)
            iksquash.append(md05)
            
            cmds.connectAttr(ikcnts[count-1]+'.worldMatrix[0]',
                             dist+'.inMatrix1')
            cmds.connectAttr(ikcnts[count]+'.worldMatrix[0]',
                             dist+'.inMatrix2')
            
            cmds.setAttr(md01+'.operation',2)
            cmds.connectAttr(dist+'.distance',md01+'.input1X')
            cmds.connectAttr(plug+'.sx',md01+'.input2X')
            
            cmds.setAttr(md02+'.operation',2)
            cmds.setAttr(md02+'.input2X',
                         cmds.getAttr(dist+'.distance'))
            cmds.connectAttr(md01+'.outputX',md02+'.input1X')
            
            cmds.setAttr(blend+'.color2R',1)
            cmds.connectAttr(md02+'.outputX',blend+'.color1R')
            cmds.connectAttr(extraCNT+'.squashStretch',
                             blend+'.blender')
            
            cmds.setAttr(md03+'.operation',3)
            cmds.setAttr(md03+'.input2X',0.5)
            cmds.connectAttr(blend+'.outputR',md03+'.input1X')
            
            cmds.setAttr(md04+'.operation',2)
            cmds.setAttr(md04+'.input1X',1)
            cmds.connectAttr(md03+'.outputX',md04+'.input2X')
            
            cmds.setAttr(fc+'.varyTime',count)
            cmds.connectAttr(plug+'.squashStretch',
                             fc+'.stream')
            cmds.setAttr(md05+'.operation',3)
            cmds.connectAttr(fc+'.varying',md05+'.input2X')
            cmds.connectAttr(md04+'.outputX',md05+'.input1X')
            
            cmds.connectAttr(blend+'.outputR',ik+'.sx')
            cmds.connectAttr(md05+'.outputX',ik+'.sy')
            cmds.connectAttr(md05+'.outputX',ik+'.sz')
    
    #setup blending
    cmds.addAttr(extraCNT,ln='FKIK',at='float',
                 keyable=True,min=0,max=1)
    
    fkikREV=cmds.shadingNode('reverse',asUtility=True,
                             n=prefix+'fkikREV')
    
    cmds.connectAttr(extraCNT+'.FKIK',fkikREV+'.inputX')
    
    ikjnts=[ikjnts[0]]
    for cnt in iktwistcnts:
        ikjnts.append(cnt)
    
    ikjnts.append(endJNT)
    
    #changing last fk joint
    
    fkjnts[-1]=endFk
    print fkjnts
    
    for jnt in jnts:
        count=jnts.index(jnt)
        
        #orient blending
        orientCon=cmds.orientConstraint(ikjnts[count],
                                        fkjnts[count],
                                        jnt)[0]
        
        cmds.connectAttr(fkikREV+'.outputX',
                         orientCon+'.'+fkjnts[count]+'W1')
        cmds.connectAttr(extraCNT+'.FKIK',
                         orientCon+'.'+ikjnts[count]+'W0')
    
    for jnt in jnts[0:-1]:
        count=jnts.index(jnt)
        
        #scale x blending
        blend=cmds.shadingNode('blendColors',asUtility=True,
                                n=prefix+'blend')
        stretch=cmds.shadingNode('blendColors',asUtility=True,
                                 n=prefix+'stretch')
        
        cmds.setAttr(blend+'.color2R',1)
        cmds.connectAttr(extraCNT+'.FKIK',blend+'.blender')
        cmds.connectAttr(ikblend[count]+'.outputR',
                         blend+'.color1R')
        
        cmds.setAttr(stretch+'.color2R',1)
        cmds.connectAttr(extraCNT+'.squashStretch',
                         stretch+'.blender')
        cmds.connectAttr(blend+'.outputR',
                         stretch+'.color1R')
        cmds.connectAttr(stretch+'.outputR',
                         jnt+'.sx')
        
        #scale yz blending
        blend=cmds.shadingNode('blendColors',asUtility=True,
                                n=prefix+'blend')
        stretch=cmds.shadingNode('blendColors',asUtility=True,
                                 n=prefix+'stretch')
        
        cmds.setAttr(blend+'.color2R',1)
        cmds.connectAttr(extraCNT+'.FKIK',blend+'.blender')
        cmds.connectAttr(iksquash[count]+'.outputX',
                         blend+'.color1R')
        
        cmds.setAttr(stretch+'.color2R',1)
        cmds.connectAttr(extraCNT+'.squashStretch',
                         stretch+'.blender')
        cmds.connectAttr(blend+'.outputR',
                         stretch+'.color1R')
        cmds.connectAttr(stretch+'.outputR',
                         jnt+'.sy')
        cmds.connectAttr(stretch+'.outputR',
                         jnt+'.sz')
    
    #visibility blending
    for cnt in fkcnts:
        cmds.connectAttr(fkikREV+'.outputX',cnt+'.v')
    
    for cnt in ikhighcnts:
        cmds.connectAttr(extraCNT+'.FKIK',cnt+'.v')
    
    #position blending
    pCon=cmds.pointConstraint(ikjnts[0],fkjnts[0],jnts[0])[0]
    
    cmds.connectAttr(fkikREV+'.outputX',
                     pCon+'.'+fkjnts[0]+'W1')
    cmds.connectAttr(extraCNT+'.FKIK',
                     pCon+'.'+ikjnts[0]+'W0')
    
    #create hip
    hipCNT=''
    
    if hipsAttach and spineType=='spine':
        #create hip jnt
        cmds.select(cl=True)
        jnt=cmds.joint(position=(0,0,0),name=prefix+'hip_jnt')
        
        cmds.container(asset,e=True,addNode=jnt)
        
        #setup jnt
        
        meta=mum.SetData('meta_'+jnt, 'joint', 'hip', module, None)
        mum.SetTransform(jnt, meta)
        
        mru.Snap(masterCNT,jnt)
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
        
        hipCNT=cnt
        
        #setup hip control
        mru.Snap(jnt,grp)
        mru.Snap(jnts[0], grp,orient=False)
        
        cmds.parent(jnt,cnt)
        cmds.parent(grp,plug)
        
        cmds.move(-spineLength/3,0,0,cnt+'.cv[0:7]',
                  r=True,os=True)
        
        #setup hip extra control
        cmds.addAttr(extraCNT,ln='hipFollow',at='float',
                     keyable=True,min=0,max=1)
        
        hipREV=cmds.shadingNode('reverse',asUtility=True,
                                 n=prefix+'hipREV')
        
        cmds.connectAttr(extraCNT+'.hipFollow',
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
        
        cmds.connectAttr(extraCNT+'.hipFollow',
                         pCon+'.'+parentGRP+'W0')
        cmds.connectAttr(hipREV+'.outputX',
                         pCon+'.'+pointGRP+'W1')
        
        #clean channel box
        attrs=['tx','ty','tz','sx','sy','sz','v']
        mru.ChannelboxClean(cnt, attrs)
    
    #clean channel box
    cnts=[]
    
    attrs=['v']
    for cnt in fkcnts:
        mru.ChannelboxClean(cnt, attrs)
        
        cnts.append(cnt)
    
    attrs=['sx','sy','sz','v']
    for cnt in ikcnts:
        mru.ChannelboxClean(cnt, attrs)
        
        cnts.append(cnt)

    attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
    mru.ChannelboxClean(extraCNT, attrs)
    
    cnts.append(extraCNT)
    
    attrs=['tx','ty','tz','ry','rz','sx','sy','sz','v']
    for cnt in iktwistcnts:
        mru.ChannelboxClean(cnt,attrs)
        
        cnts.append(cnt)
    
    #publishing controllers
    cnts.append(masterCNT)
    cnts.append(hipCNT)
    
    for cnt in cnts:
        cmds.container(asset,e=True,addNode=[cnt])
        cmds.containerPublish(asset,publishNode=(cnt,''))
        cmds.containerPublish(asset,bindNode=(cnt,cnt))

'''
templateModule='meta_spine'
Rig(templateModule)
'''