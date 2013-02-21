import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru

def fkSwitch():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #error checking for selection count
    nodeSelection=cmds.ls(selection=True)
    
    if len(nodeSelection)>=1:
        for node in nodeSelection:
            #travel upstream and finding the module
            module=mum.UpStream(node, 'module')
            
            #switching to fk with extra control and finding fk cnts
            cnts=mum.DownStream(module, 'control')
            for cnt in cnts:
                data=mum.GetData(cnt)
                
                if data['component']=='extra':
                    transformNode=mum.GetTransform(cnt)
                    
                    cmds.setAttr(transformNode+'.FKIK',0)
            
            #finding fk cnts
            filterData={'system':'fk'}
            fkcnts=mum.Filter(cnts, filterData)
            
            #transforming fk cnts to their switch node
            for cnt in mum.Sort(fkcnts, 'index'):
                data=mum.GetData(cnt)
                
                switch=data['switch']
                transformNode=mum.GetTransform(cnt)
                
                mru.Snap(switch, transformNode)
    else:
        cmds.warning('Nothing is selected!')
    
    cmds.undoInfo(closeChunk=True)

def ikSwitch():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #error checking for selection count
    nodeSelection=cmds.ls(selection=True)
    
    if len(nodeSelection)>=1:
        for node in nodeSelection:
            #travel upstream and finding the module
            module=mum.UpStream(node, 'module')
            
            #finding cnts and switching to ik with extra control
            cnts=mum.DownStream(module, 'control')
            
            for cnt in cnts:
                data=mum.GetData(cnt)
                
                if data['component']=='extra':
                    transformNode=mum.GetTransform(cnt)
                    
                    cmds.setAttr(transformNode+'.FKIK',1)
            
            #finding ik cnts
            filterData={'system':'ik'}
            ikcnts=mum.Filter(cnts, filterData)
            
            #transforming ik cnts to their switch node
            for cnt in mum.Sort(ikcnts, 'index'):
                data=mum.GetData(cnt)
                
                switch=data['switch']
                transformNode=mum.GetTransform(cnt)
                
                mru.Snap(switch, transformNode)
    else:
        cmds.warning('Nothing is selected!')
    
    cmds.undoInfo(closeChunk=True)