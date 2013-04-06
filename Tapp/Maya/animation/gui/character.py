import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru

def FkSwitch():
    __switch__('fk')

def IkSwitch():
    __switch__('ik')

def __switch__(mode):
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #error checking for selection count
    nodeSelection=cmds.ls(selection=True)
    
    if len(nodeSelection)>=1:
        #getting modules
        modules=[]
        for node in nodeSelection:
            
            modules.append(mum.UpStream(node, 'module'))
        
        modules=set(modules)
        
        #module loop
        for module in modules:
            #finding cnts and switching to ik with extra control
            cnts=mum.DownStream(module, 'control')
            
            for cnt in cnts:
                data=mum.GetData(cnt,stripNamespace=False)
                
                if data['component']=='extra':
                    transformNode=mum.GetTransform(cnt)
                    
                    if mode=='ik':
                        cmds.setAttr(transformNode+'.FKIK',1)
                    if mode=='fk':
                        cmds.setAttr(transformNode+'.FKIK',0)
            
            #finding ik cnts
            if mode=='ik':
                filterData={'system':'ik'}
            if mode=='fk':
                filterData={'system':'fk'}
            ikcnts=mum.Filter(cnts, filterData)
            
            #transforming ik cnts to their switch node
            for cnt in mum.Sort(ikcnts, 'index'):
                data=mum.GetData(cnt,stripNamespace=False)
                
                switch=data['switch']
                transformNode=mum.GetTransform(cnt)
                
                mru.Snap(switch, transformNode,scale=True)
                
                #scale switching
                transscl=mru.GetWorldScale(transformNode)
                transscl=mru.RoundList(transscl, 9)
                switchscl=mru.GetWorldScale(switch)
                switchscl=mru.RoundList(switchscl, 9)
                
                scl=[1,1,1]
                for count in xrange(0,3):
                    if transscl[count]!=switchscl[count]:
                        
                        scl[count]=switchscl[count]/transscl[count]
                
                cmds.xform(transformNode,r=True,scale=scl)
    else:
        cmds.warning('Nothing is selected!')
    
    cmds.undoInfo(closeChunk=True)

def __zeroNode__(node):
    if (cmds.getAttr('%s.tx' % node,lock=True))!=True:
        cmds.setAttr('%s.tx' % node,0)
    if (cmds.getAttr('%s.ty' % node,lock=True))!=True:
        cmds.setAttr('%s.ty' % node,0)
    if (cmds.getAttr('%s.tz' % node,lock=True))!=True:
        cmds.setAttr('%s.tz' % node,0)
    if (cmds.getAttr('%s.rx' % node,lock=True))!=True:
        cmds.setAttr('%s.rx' % node,0)
    if (cmds.getAttr('%s.ry' % node,lock=True))!=True:
        cmds.setAttr('%s.ry' % node,0)
    if (cmds.getAttr('%s.rz' % node,lock=True))!=True:
        cmds.setAttr('%s.rz' % node,0)

def ZeroControl():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero controls
    if len(sel)>=1:
        for node in cmds.ls(sl=True):
            __zeroNode__(node)
        
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def ZeroLimb():
    #failsafe on non-modular nodes selected
    
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero limb
    if len(sel)>=1:
        modules=[]
        for node in sel:
            modules.append(mum.UpStream(node, 'module'))
        
        if len(modules)>=1:
            modules=set(modules)
            for module in modules:
                cnts=mum.DownStream(module, 'control')
                
                for cnt in cnts:
                    tn=mum.GetTransform(cnt)
                    
                    __zeroNode__(tn)
        else:
            cmds.warning('Could not find any limbs connected to the selected nodes.')
        
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def ZeroCharacter():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero character
    if len(sel)>=1:
        root=mum.UpStream(sel[0], 'root')
        
        if root!=None:
            cnts=mum.DownStream(root, 'control', allNodes=True)
            for cnt in cnts:
                tn=mum.GetTransform(cnt)
                
                __zeroNode__(tn)
        else:
            cmds.warning('Could not find any character connected to the selected nodes.')
    
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def KeyLimb():
    
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #key limb
    if len(sel)>=1:
        modules=[]
        for node in sel:
            modules.append(mum.UpStream(node, 'module'))
        
        if len(modules)>=1:
            modules=set(modules)
            for module in modules:
                cnts=mum.DownStream(module, 'control')
                
                for cnt in cnts:
                    tn=mum.GetTransform(cnt)
                    
                    cmds.setKeyframe(tn)
        else:
            cmds.warning('Could not find any limbs connected to the selected nodes.')
        
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def KeyCharacter():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero character
    if len(sel)>=1:
        root=mum.UpStream(sel[0], 'root')
        
        if root!=None:
            cnts=mum.DownStream(root, 'control', allNodes=True)
            for cnt in cnts:
                tn=mum.GetTransform(cnt)
                
                cmds.setKeyframe(tn)
        else:
            cmds.warning('Could not find any character connected to the selected nodes.')
        
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def SelectLimb():
    
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #key limb
    if len(sel)>=1:
        modules=[]
        for node in sel:
            modules.append(mum.UpStream(node, 'module'))
        
        cmds.select(cl=True)
        
        if len(modules)>=1:
            modules=set(modules)
            for module in modules:
                cnts=mum.DownStream(module, 'control')
                
                for cnt in cnts:
                    tn=mum.GetTransform(cnt)
                    
                    cmds.select(tn,add=True)
        else:
            cmds.warning('Could not find any limbs connected to the selected nodes.')
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def SelectCharacter():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero character
    if len(sel)>=1:
        root=mum.UpStream(sel[0], 'root')
        
        cmds.select(cl=True)
        
        if root!=None:
            cnts=mum.DownStream(root, 'control', allNodes=True)
            for cnt in cnts:
                tn=mum.GetTransform(cnt)
                
                cmds.select(tn,add=True)
        else:
            cmds.warning('Could not find any character connected to the selected nodes.')
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)