import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils.utils as mruu

class Joint():
    ''' Class for all joint module related functions. '''
    
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
        meta=mum.Meta()
        ucs=mruu.ControlShape()
        
        #collect all components
        controls=meta.DownStream(module,'control')
        
        for control in controls:
            data=meta.GetData(control)
            
            if data['component']=='joint':
                jnt=meta.GetTransform(control)
        
        #getting transform data
        jntTrans=cmds.xform(jnt,worldSpace=True,query=True,
                              translation=True)
        jntRot=cmds.xform(jnt,worldSpace=True,query=True,
                          rotation=True)
        
        #getting module data
        data=meta.GetData(module)
        
        controlShape=data['controlShape']
        
        #establish side
        side='center'
        
        x=jntTrans[0]
        
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
        cmds.delete(cmds.container(q=True,fc=jnt))
        
        #establish prefix and suffix
        prefix=side[0]+'_'+'joint'+str(index)+'_'
        suffix='_'+side[0]+'_'+'joint'+str(index)
        
        #creating asset
        asset=cmds.container(n=prefix+'rig')
        
        #create module
        data={'side':side,'index':str(index),'system':'rig'}
        
        module=meta.SetData(('meta'+suffix),'module','joint',None,
                            data)
        
        cmds.container(asset,e=True,addNode=module)
        
        #create plug
        plug=cmds.spaceLocator(name=prefix+'plug')[0]
        
        phgrp=cmds.group(plug,n=(plug+'_PH'))
        sngrp=cmds.group(plug,n=(plug+'_SN'))
        
        metaParent=meta.SetData('meta_'+plug,'plug',None,module,
                                None)
        
        meta.SetTransform(plug, metaParent)
        
        cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
        
        #create control
        if controlShape=='Square':
            cnt=ucs.Square(prefix+'cnt')
        if controlShape=='FourWay':
            cnt=ucs.FourWay(prefix+'cnt')
        if controlShape=='Circle':
            cnt=ucs.Circle(prefix+'cnt')
        if controlShape=='Box':
            cnt=ucs.Box(prefix+'cnt')
        if controlShape=='Pin':
            cnt=ucs.Pin(prefix+'cnt')
        if controlShape=='Sphere':
            cnt=ucs.Sphere(prefix+'cnt')
        
        cmds.container(asset,e=True,addNode=cnt)
        
        #create joint
        jnt=cmds.joint(n=prefix+'jnt')
        
        cmds.container(asset,e=True,addNode=jnt)
        
        #create socket
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        cmds.container(asset,e=True,addNode=socket)
        
        #setup socket
        cmds.parent(socket,jnt)
        
        data={'index':1}
        metaParent=meta.SetData('meta_'+socket,'socket',None,
                                module,data)
        meta.SetTransform(socket, metaParent)
        
        #setup control
        cmds.parent(cnt,plug)
        
        mNode=meta.SetData(('meta_'+cnt),'control','joint',
                           module,None)
        meta.SetTransform(cnt, mNode)
        
        #setup plug
        cmds.xform(phgrp,ws=True,translation=jntTrans)
        cmds.xform(phgrp,ws=True,rotation=jntRot)
        
templateModule='meta_joint'

joint=Joint()
joint.Rig(templateModule)