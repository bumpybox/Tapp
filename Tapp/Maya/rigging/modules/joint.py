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
                     namespace='joint')

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
        
        if data['component']=='joint':
            jnt=mum.GetTransform(control)
    
    #getting transform data
    jntTrans=cmds.xform(jnt,worldSpace=True,query=True,
                          translation=True)
    jntRot=cmds.xform(jnt,worldSpace=True,query=True,
                      rotation=True)
    
    #getting module data
    data=mum.GetData(module)
    
    controlShape=data['controlShape']
    inheritName=data['inheritName']
    
    #establish side
    side='center'
    
    x=jntTrans[0]
    
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
    
    #establish module name
    moduleName='joint'
    
    if inheritName=='True':
        moduleName=cmds.container(q=True,fc=jnt)
        
        moduleName=moduleName.split(':')[-1]
    
    #delete template
    cmds.delete(cmds.container(q=True,fc=jnt))
    
    #establish prefix and suffix
    prefix=side[0]+'_'+moduleName+str(index)+'_'
    suffix='_'+side[0]+'_'+moduleName+str(index)
    
    #creating asset
    asset=cmds.container(n=prefix+'rig')
    
    #create module
    data={'side':side,'index':str(index),'system':'rig','subcomponent':'joint'}
    
    module=mum.SetData(('meta'+suffix),'module','joint',None,
                        data)
    
    cmds.container(asset,e=True,addNode=module)
    
    #create plug
    plug=cmds.spaceLocator(name=prefix+'plug')[0]
    
    phgrp=cmds.group(plug,n=(plug+'_PH'))
    sngrp=cmds.group(plug,n=(plug+'_SN'))
    
    metaParent=mum.SetData('meta_'+plug,'plug',None,module,
                            None)
    
    mum.SetTransform(plug, metaParent)
    
    cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
    
    #create control
    if controlShape=='Square':
        cnt=mru.Square(prefix+'cnt')
    if controlShape=='FourWay':
        cnt=mru.FourWay(prefix+'cnt')
    if controlShape=='Circle':
        cnt=mru.Circle(prefix+'cnt')
    if controlShape=='Box':
        cnt=mru.Box(prefix+'cnt')
    if controlShape=='Pin':
        cnt=mru.Pin(prefix+'cnt')
    if controlShape=='Sphere':
        cnt=mru.Sphere(prefix+'cnt')
    
    cmds.container(asset,e=True,addNode=cnt)
    
    #create joint
    jnt=cmds.joint(n=prefix+'jnt')
    
    cmds.container(asset,e=True,addNode=jnt)
    
    #setup joint
    meta=mum.SetData('meta_'+jnt, 'joint', None, module, None)
    mum.SetTransform(jnt, meta)
    
    #create socket
    socket=cmds.spaceLocator(name=prefix+'socket')[0]
    
    cmds.container(asset,e=True,addNode=socket)
    
    #setup socket
    cmds.parent(socket,jnt)
    
    data={'index':1}
    metaParent=mum.SetData('meta_'+socket,'socket',None,
                            module,data)
    mum.SetTransform(socket, metaParent)
    
    #setup control
    cmds.parent(cnt,plug)
    
    mNode=mum.SetData(('meta_'+cnt),'control','joint',
                       module,None)
    mum.SetTransform(cnt, mNode)
    
    #setup plug
    cmds.xform(phgrp,ws=True,translation=jntTrans)
    cmds.xform(phgrp,ws=True,rotation=jntRot)
    
    #publishing controllers
    cmds.containerPublish(asset,publishNode=(cnt,''))
    cmds.containerPublish(asset,bindNode=(cnt,cnt))

'''
templateModule='tegan_template:joint:meta_joint1'
Rig(templateModule)
'''