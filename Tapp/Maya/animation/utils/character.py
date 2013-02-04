import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils.utils as mruu

def fkSwitch():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #class variables
    meta=mum.Meta()
    ut=mruu.Transform()
    
    #error checking for selection count
    nodeSelection=cmds.ls(selection=True)
    
    if len(nodeSelection)>=1:
        for node in nodeSelection:
            #travel upstream and finding the module
            module=meta.UpStream(node, 'module')
            
            #switching to fk with extra control and finding fk cnts
            cnts=meta.DownStream(module, 'control')
            for cnt in cnts:
                data=meta.GetData(cnt)
                
                if data['component']=='extra':
                    transformNode=meta.GetTransform(cnt)
                    
                    cmds.setAttr(transformNode+'.FKIK',0)
            
            #finding fk cnts
            filterData={'system':'fk'}
            fkcnts=meta.Filter(cnts, filterData)
            
            #transforming fk cnts to their switch node
            for cnt in meta.Sort(fkcnts, 'index'):
                data=meta.GetData(cnt)
                
                switch=data['switch']
                transformNode=meta.GetTransform(cnt)
                
                ut.Snap(switch, transformNode)
    else:
        cmds.warning('Nothing is selected!')
    
    cmds.undoInfo(closeChunk=True)

def ikSwitch():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #class variables
    meta=mum.Meta()
    ut=mruu.Transform()
    
    #error checking for selection count
    nodeSelection=cmds.ls(selection=True)
    
    if len(nodeSelection)>=1:
        for node in nodeSelection:
            #travel upstream and finding the module
            module=meta.UpStream(node, 'module')
            
            #finding cnts and switching to ik with extra control
            cnts=meta.DownStream(module, 'control')
            
            for cnt in cnts:
                data=meta.GetData(cnt)
                
                if data['component']=='extra':
                    transformNode=meta.GetTransform(cnt)
                    
                    cmds.setAttr(transformNode+'.FKIK',1)
            
            #finding ik cnts
            filterData={'system':'ik'}
            ikcnts=meta.Filter(cnts, filterData)
            
            #transforming ik cnts to their switch node
            for cnt in meta.Sort(ikcnts, 'index'):
                data=meta.GetData(cnt)
                
                switch=data['switch']
                transformNode=meta.GetTransform(cnt)
                
                ut.Snap(switch, transformNode)
    else:
        cmds.warning('Nothing is selected!')
    
    cmds.undoInfo(closeChunk=True)