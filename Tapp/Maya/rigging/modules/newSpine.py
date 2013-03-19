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
    asset=cmds.container(n=prefix+'rig',type='dagContainer')
    
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
    
    #create jnts
    jnts=[]
    sockets=[]
    
    for count in xrange(1,jointAmount+1):
        
        print (spineLength/jointAmount+1)*count
        
        #create joint
        jnt=cmds.joint(position=((spineLength/jointAmount+1)*count,0,0),
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
    
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=endTrans)
    
    cmds.xform(jnts[0],worldSpace=True,translation=startTrans)
    cmds.delete(cmds.aimConstraint(grp,jnts[0],
                                  worldUpVector=(1,0,0)))
    
    cmds.delete(grp)
    
templateModule='spine:meta_spine'
Rig(templateModule)
