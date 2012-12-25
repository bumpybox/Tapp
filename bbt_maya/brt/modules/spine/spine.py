import maya.cmds as cmds
import maya.mel as mel

from bbt_maya import generic
from bbt_maya.brt.modules import utils
from bbt_maya.python import ZvParentMaster as zv

class Spine():
    ''' Class for all limb related functions. '''
    
    def Create(self):
        pass
    
    def Import(self):
        pass
    
    def Attach(self,sourceModule,targetModule):
        pass
    
    def Detach(self,module):
        pass
    
    def Rig(self,module):
        ''' Rigs the provided module. '''
        
        #class variables
        meta=generic.Meta()
        ut=utils.Transform()
        ucs=utils.ControlShape()
        um=utils.Math()
        
        #collect all components
        controls=meta.DownStream(module,'control')
        
        for control in controls:
            if meta.GetData(control)['component']=='start':
                start=meta.GetTransform(control)
            if meta.GetData(control)['component']=='line':
                line=meta.GetTransform(control)
            if meta.GetData(control)['component']=='end':
                end=meta.GetTransform(control)
        
        #getting module data
        data=meta.GetData(module)
        
        jointAmount=data['joints']
        
        #getting transform data
        startTrans=cmds.xform(start,worldSpace=True,query=True,
                              translation=True)
        startRot=cmds.xform(start,worldSpace=True,query=True,
                          rotation=True)
        endTrans=cmds.xform(end,worldSpace=True,query=True,
                            translation=True)
        endRot=cmds.xform(end,worldSpace=True,query=True,
                          rotation=True)
        
        #NEED TO GET JOINTS TRANSLATION DATA
        
        #establish side
        side='center'
        
        x=(startTrans[0]+endTrans[0])/2
        
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
            'component' in data.keys() and \
            data['type']=='module' and \
            data['side']==side and \
            data['index']==index:
                index+=1
        
        #delete template
        cmds.delete(cmds.container(q=True,fc=start))
        
        #establish prefix and suffix
        prefix=side[0]+'_'+'spine'+str(index)+'_'
        suffix='_'+side[0]+'_'+'spine'+str(index)
        
        #creating asset
        asset=cmds.container(n=prefix+'rig')
        
        #create module
        data={'side':side,'index':str(index),'system':'rig'}
        
        module=meta.SetData(('meta'+suffix),'module','spine',None,
                            data)
        
        cmds.container(asset,e=True,addNode=module)
        
        #create plug
        plug=cmds.spaceLocator(name=prefix+'plug')[0]
        
        phgrp=cmds.group(plug,n=(plug+'_PH'))
        sngrp=cmds.group(plug,n=(plug+'_SN'))
        
        cmds.xform(phgrp,worldSpace=True,translation=startTrans)
        
        metaParent=meta.SetData('meta_'+plug,'plug',None,module,
                                None)
        
        meta.SetTransform(plug, metaParent)
        
        cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])

templateModule='meta_spine'

spine=Spine()
spine.Rig(templateModule)