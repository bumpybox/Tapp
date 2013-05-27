'''

- start attrs
- end attrs

'''

import maya.cmds as cmds


def traverse(obj):
    
    result=[]
    
    def iterer(obj,level=1):
    
        objDict={}
        
        objDict['attr']=cmds.listAttr(obj,userDefined=True)
        objDict['name']=obj
        objDict['level']=level
        
        result.append(objDict)
        
        for child in cmds.listRelatives(obj,children=True):
            
            if cmds.nodeType(child)=='transform':
                
                iterer(child,level+1)
    
    iterer(obj)
    
    return result

def attr_occurence(chain,startAttrs,endAttrs,occurence):
    
    levels=[]
    
    for obj in chain:
        
        if len(set(obj['attr']) & set(startAttrs))>0:
            levels.append(obj['level'])
    
    match=[]
    
    objMax={}
    objMin={}
    
    for obj in chain:
        if obj['level']==min(levels) and len(set(obj['attr']) & set(startAttrs))>0:
            
            objMin=obj
            
        if obj['level']==max(levels) and len(set(obj['attr']) & set(startAttrs))>0:
            
            objMax=obj
    
    for obj in chain:
        if obj['level']>=objMin['level'] and obj['level']<=objMax['level']:
            
            match.append(obj)
        
    if occurence=='min':
        return match[0]
    if occurence=='max':
        return match[-1]
    if occurence=='mid':
        return match
    

#storing selection
sel=cmds.ls(selection=True)

points=cmds.ls(assemblies=True)

chains=[]
for p in points:
    
    shape=cmds.listRelatives(p,shapes=True)
    if cmds.nodeType(shape)=='implicitBox':
        
        chains.append(traverse(p))

#restoring selection
if sel:
    cmds.select(sel)
else:
    cmds.select(cl=True)

#data analysis
for c in chains:
    
    startAttrs=['IK_control','IK_solver_start']
    endAttrs=['IK_solver_end']
    print attr_occurence(c,startAttrs,'mid')