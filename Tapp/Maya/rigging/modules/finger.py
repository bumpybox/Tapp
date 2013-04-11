import collections

import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru

def Create():
    
    result = cmds.promptDialog(
            title='Amount of finger joints?',
            message='Enter Amount:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')
    
    if result == 'OK':
        text = cmds.promptDialog(query=True, text=True)
        __create__(int(text))

def __createMirror__(module):
    
    jointAmount=len(mum.DownStream(module, 'control'))-1
    
    return __create__(jointAmount)

def __create__(jointAmount):
    ''' Creates the finger module. '''
    
    cmds.undoInfo(openChunk=True)
    
    #creating asset
    asset=cmds.container(n='finger')
    
    #setup asset
    cmds.addAttr(asset,ln='index',at='long',defaultValue=1,keyable=True)
    
    cmds.setAttr(asset+'.blackBox',True)
    
    #create module
    data={'system':'template'}
    
    module=mum.SetData(('meta_'+asset),'root','finger',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #setup module
    cmds.addAttr(module,ln='index',at='long',defaultValue=1)
    
    cmds.connectAttr(asset+'.index',module+'.index')
    
    #control collection
    cnts=[]
    
    #create root control
    root=mru.Sphere(asset+'_root_cnt')
    
    cmds.container(asset,e=True,addNode=root)
    
    #setup base control
    data={'index':0}
    mNode=mum.SetData(('meta_'+root),'control','root',module,
                        data)
    mum.SetTransform(root, mNode)
    
    cnts.append(root)
    
    cmds.move(-3,0,0,root)
    
    #create base control
    base=mru.Box(asset+'_base_cnt')
    
    cmds.container(asset,e=True,addNode=base)
    
    #setup base control
    data={'index':1}
    mNode=mum.SetData(('meta_'+base),'control','base',module,
                        data)
    mum.SetTransform(base, mNode)
    
    cnts.append(base)
    
    cmds.parent(root,base)
    
    #create jnts
    jnts=[]
    metas=[mNode]
    
    for count in xrange(1,jointAmount):
        #create control
        cnt=mru.Sphere(asset+'_joint'+str(count)+'_cnt')
        
        cmds.container(asset,e=True,addNode=cnt)
        
        #setup control
        data={'index':count+1}
        mNode=mum.SetData(('meta_'+cnt),'control','joint',
                           module,data)
        mum.SetTransform(cnt, mNode)
        
        metas.append(mNode)
        
        cmds.xform(cnt,ws=True,translation=[count*3,0,0])
        
        cmds.parent(cnt,base)
        
        jnts.append(cnt)
        cnts.append(cnt)
    
    #create end control
    end=mru.Sphere(asset+'_end_cnt')
    
    cmds.container(asset,e=True,addNode=end)
    
    #setup end control
    data={'index':int(jointAmount)+1}
    mNode=mum.SetData(('meta_'+end),'control','end',module,
                        data)
    mum.SetTransform(end, mNode)
    
    metas.append(mNode)
    
    cmds.xform(end,ws=True,translation=[jointAmount*3,0,0])
    
    cmds.parent(end,base)
    
    cnts.append(end)
    
    #create line
    pos=[]
    
    for cnt in cnts:
        pos.append(cmds.xform(cnt,q=True,ws=True,
                              translation=True))
    
    line=cmds.curve(d=1,p=pos,n='fingerLine')
    
    cmds.container(asset,e=True,addNode=line)
    
    #setup line
    for count in xrange(0,jointAmount+2):
        cmds.select(line+'.cv['+str(count)+']',r=True)
        cluster=mel.eval('newCluster " -envelope 1";')[1]
        
        cmds.parent(cluster,cnts[count])
        cmds.setAttr(cluster+'.v',False)
    
    cmds.setAttr(line+'.overrideEnabled',1)
    cmds.setAttr(line+'.overrideDisplayType',2)
    
    #publish controls
    for cnt in cnts:
        cmds.container(asset,e=True,addNode=[cnt])
        cmds.containerPublish(asset,publishNode=(cnt,''))
        cmds.containerPublish(asset,bindNode=(cnt,cnt))
    
    #clear selection
    cmds.select(cl=True)
    
    cmds.undoInfo(closeChunk=True)
    
    #return
    return metas

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
    
    jnts=[]
    
    for control in controls:
        if mum.GetData(control)['component']=='base':
            base=mum.GetTransform(control)
        if mum.GetData(control)['component']=='root':
            root=mum.GetTransform(control)
        if mum.GetData(control)['component']=='joint':
            jnts.append(mum.GetTransform(control))
        if mum.GetData(control)['component']=='end':
            end=mum.GetTransform(control)
    
    #sorting jnts
    jnts=mum.Sort(jnts, 'index')
    
    #getting transform data
    jntsTrans=[]
    
    rootTrans=cmds.xform(root,worldSpace=True,query=True,
                          translation=True)
    baseTrans=cmds.xform(base,worldSpace=True,query=True,
                          translation=True)
    baseRot=cmds.xform(base,worldSpace=True,query=True,
                          rotation=True)
    endTrans=cmds.xform(end,worldSpace=True,query=True,
                        translation=True)
    for jnt in jnts:
        jntsTrans.append(cmds.xform(jnt,worldSpace=True,
                                      query=True,
                                      translation=True))
    
    #establish side
    side='center'
    
    x=(baseTrans[0]+endTrans[0])/2
    
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
    cmds.delete(cmds.container(q=True,fc=base))
    
    #establish prefix and suffix
    prefix=side[0]+'_'+'finger'+str(index)+'_'
    suffix='_'+side[0]+'_'+'finger'+str(index)
    
    #initial setup---
    
    #creating asset
    asset=cmds.container(n=prefix+'rig',type='dagContainer')
    
    attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
    mru.ChannelboxClean(asset, attrs)
    
    #create module
    data={'side':side,'index':str(index),'system':'rig','subcomponent':'finger'}
    
    module=mum.SetData(('meta'+suffix),'module','finger',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #create plug
    plug=cmds.spaceLocator(name=prefix+'plug')[0]
    
    phgrp=cmds.group(empty=True,n=(plug+'_PH'))
    sngrp=cmds.group(empty=True,n=(plug+'_SN'))
    
    cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
    
    cmds.parent(sngrp,phgrp)
    cmds.parent(plug,sngrp)
    
    cmds.xform(phgrp,worldSpace=True,translation=baseTrans)
    
    metaParent=mum.SetData('meta_'+plug,'plug',None,module,
                            None)
    
    mum.SetTransform(plug, metaParent)
    
    #create jnts---
    
    #create base joint
    baseJNT=cmds.joint(position=(baseTrans[0],baseTrans[1],
                                 baseTrans[2]),
                       name=prefix+'jnt1')
    
    cmds.container(asset,e=True,addNode=baseJNT)
    
    #setup base joint
    meta=mum.SetData('meta_'+baseJNT, 'joint', 'base', module, None)
    mum.SetTransform(baseJNT, meta)
    
    cmds.xform(baseJNT,worldSpace=True,translation=baseTrans)
    
    cmds.xform(baseJNT,ws=True,rotation=baseRot)
    
    cmds.makeIdentity(baseJNT,apply=True,t=1,r=1,s=1,n=0)
    
    #create root joint
    cmds.select(cl=True)
    rootJNT=cmds.joint(position=(rootTrans[0],rootTrans[1],
                                 rootTrans[2]),
                       name=prefix+'jnt0')
    
    cmds.container(asset,e=True,addNode=rootJNT)
    
    #setup root joint
    meta=mum.SetData('meta_'+baseJNT, 'joint', 'root', module, None)
    mum.SetTransform(rootJNT, meta)
    
    cmds.xform(rootJNT,worldSpace=True,translation=rootTrans)
    
    aimCon=cmds.aimConstraint(baseJNT,
                              rootJNT,
                              worldUpType='objectrotation',
                              aimVector=[1,0,0],
                              upVector=[0,1,0],
                              worldUpVector=[0,1,0],
                              worldUpObject=baseJNT)
    
    cmds.delete(aimCon)
    
    #create end joint
    cmds.select(cl=True)
    endJNT=cmds.joint(position=(endTrans[0],endTrans[1],
                                 endTrans[2]),
                       name=prefix+'jnt'+str(len(jnts)+2))
    
    cmds.container(asset,e=True,addNode=endJNT)
    
    #setup end joint
    cmds.xform(endJNT,worldSpace=True,translation=endTrans)
    
    cmds.makeIdentity(endJNT,apply=True,t=1,r=1,s=1,n=0)
    
    #create individual joints
    jnts=[]
    
    for pos in jntsTrans:
        count=jntsTrans.index(pos)+2
        
        #create joint
        cmds.select(cl=True)
        jnt=cmds.joint(position=(0,0,0),
                       name=prefix+'jnt'+str(count))
        
        cmds.container(asset,e=True,addNode=jnt)
        
        #setup joint
        meta=mum.SetData('meta_'+jnt, 'joint', None, module, None)
        mum.SetTransform(jnt, meta)
        
        cmds.xform(jnt,worldSpace=True,translation=pos)
        
        jnts.append(jnt)
    
    jnts.append(endJNT)
    
    #setup jnts
    for count in xrange(1,len(jnts)):
        aimCon=cmds.aimConstraint(jnts[count],
                                  jnts[count-1],
                                  worldUpType='objectrotation',
                                  aimVector=[1,0,0],
                                  upVector=[0,1,0],
                                  worldUpVector=[0,1,0],
                                  worldUpObject=baseJNT)
        
        cmds.delete(aimCon)
    
    mru.Snap(jnts[len(jnts)-2], endJNT, point=False)
    
    #adding base joint to jnts
    q = collections.deque(jnts)
    q.appendleft(baseJNT)
    q.appendleft(rootJNT)
    
    jnts=[]
    for item in q:
        jnts.append(item)
    
    del jnts[-1]
    
    #create fk---
    #controls
    cnts=[]
    cntsGRP=[]
    cntsgrpGRP=[]
    
    for jnt in jnts:
        count=jnts.index(jnt)+1
        
        #create control
        if count==1:
            cnt=mru.Pin(prefix+str(count)+'_cnt')
        else:
            cnt=mru.Square(prefix+str(count)+'_cnt')
        
        cmds.container(asset,e=True,addNode=cnt)
        
        #setup control
        data={'index':count}
        mNode=mum.SetData(('meta_'+cnt),'control','joint',
                           module,data)
        mum.SetTransform(cnt, mNode)
        
        grp=cmds.group(empty=True,n=(prefix+str(count)+'_grp'))
        cntGRP=cmds.group(empty=True,n=(cnt+'_grp'))
        
        cmds.container(asset,e=True,addNode=[grp,cntGRP])
        
        cmds.parent(cnt,cntGRP)
        cmds.parent(cntGRP,grp)
        
        mru.Snap(jnt,grp)
        
        cmds.parentConstraint(cnt,jnt)
        cmds.scaleConstraint(cnt,jnt)
        
        if count!=1:
            cmds.parent(grp,cnts[count-2])
        
        cntsGRP.append(cntGRP)
        cntsgrpGRP.append(grp)
        cnts.append(cnt)
    
    cmds.parent(cntsgrpGRP[0],plug)
    
    #removing end joint
    cmds.delete(endJNT)
    
    #removing root control
    rootCNT=cnts[0]
    del(cnts[0])
    del(cntsGRP[0])
    del(cntsgrpGRP[0])
    
    #base control---
    
    #create base control
    baseCNT=mru.Pin(prefix+'base_cnt')
    
    cmds.container(asset,e=True,addNode=baseCNT)
    
    #setup base control
    mNode=mum.SetData(('meta_'+baseCNT),'control','base',
                       module,None)
    mum.SetTransform(baseCNT, mNode)
    
    grp=cmds.group(empty=True,n=(baseCNT+'_grp'))
    
    cmds.container(asset,e=True,addNode=grp)
    
    cmds.parent(baseCNT,grp)
    cmds.parent(grp,rootCNT)
    
    mru.Snap(cnts[0], grp)
    
    for grp in cntsGRP:
        cmds.connectAttr(baseCNT+'.rx',grp+'.rx')
        cmds.connectAttr(baseCNT+'.ry',grp+'.ry')
        cmds.connectAttr(baseCNT+'.rz',grp+'.rz')
    
    #channelbox clean
    attrs=['sx','sy','sz','v']
    mru.ChannelboxClean(baseCNT, attrs)
    
    for cnt in cnts:
        attrs=['v']
        mru.ChannelboxClean(cnt,attrs)
    
    #publishing controllers
    cnts.append(baseCNT)
    cnts.append(rootCNT)
    
    for cnt in cnts:
        
        cmds.containerPublish(asset,publishNode=(cnt,''))
        cmds.containerPublish(asset,bindNode=(cnt,cnt))

#Create()
#templateModule='meta_finger'
#Rig(templateModule)