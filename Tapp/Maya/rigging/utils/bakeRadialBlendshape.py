import maya.cmds as cmds

_rbsAttrs = ('blend', 'twist', 'curvature')
_unnamed = '<unnamed>'
_nameSfx = ('_B', '_T', '_C')
_rbsNodeName = 'radialBlendShape'

def _getRBS(obj):
    rbsNodeList = [s for s in cmds.listHistory(obj, pdo=True, il=2) or [] if cmds.nodeType(s) == _rbsNodeName]
    return rbsNodeList and rbsNodeList[0] or None

def _getTargetIndices(rbsNode):
    return cmds.getAttr('%s.%s' % (rbsNode, _rbsAttrs[0]), mi=True) or []

def _getTargetNames(rbsNode, idx=-1):
    if idx == -1:
        idxList = _getTargetIndices(rbsNode)
        return [_getTargetNames(rbsNode, i) for i in idxList]
    
    alias = cmds.aliasAttr('%s.%s[%d]' % (rbsNode, _rbsAttrs[0], idx), q=True)
    
    if not alias:
        return _unnamed
    
    elif alias.endswith(_nameSfx[0]):
        return alias[:-len(_nameSfx[0])]
    
    return alias

accuracy=0.1

sel=cmds.ls(selection=True)
obj=sel[0]

rb=_getRBS(obj)

bs=cmds.blendShape(obj)[0]
targets=_getTargetNames(rb)

#zero attributes
for target in targets:
    
    for sfx in _nameSfx:
        
        cmds.setAttr(rb+'.'+target+sfx,0)

for target in targets:
    
    #duplicating target
    cmds.setAttr(rb+'.'+target+'_B',1)
    copy=cmds.duplicate(obj,n=target)[0]
    cmds.setAttr(rb+'.'+target+'_B',0)
    
    #adding to blendshape
    index=targets.index(target)+1
    cmds.blendShape(bs, edit=True, target=(obj, index, copy, 1))
    
    cmds.delete(copy)
    
    for step in xrange(0,9):
        
        incr=(step+1.0)/10
        
        #duplicating target
        cmds.setAttr(rb+'.'+target+'_B',incr)
        copy=cmds.duplicate(obj,n=target)[0]
        cmds.setAttr(rb+'.'+target+'_B',0)
        
        #adding to blendshape
        index=targets.index(target)+1
        cmds.blendShape(bs, edit=True,inBetween=True, target=(obj, index, copy, incr))
        
        cmds.delete(copy)