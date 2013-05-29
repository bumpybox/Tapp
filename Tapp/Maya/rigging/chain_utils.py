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
        
        objDict['children']=cmds.listRelatives(obj,children=True,fullPath=True,type='transform')
        
        parent=cmds.listRelatives(obj,parent=True,fullPath=True)
        if parent:
            objDict['parent']=parent[0]
        else:
            objDict['parent']=None
        
        result.append(objDict)
        
        for child in cmds.listRelatives(obj,children=True,fullPath=True):
            
            if cmds.nodeType(child)=='transform':
                
                iterer(child,level+1)
    
    iterer(obj)
    
    return result

def breakdown(chain,start=None,end=None):    
    
    root=chain[0]
    for node in chain:
        if node['parent']==None:
            root=node
    
    def downstream(chain,node,attr):
        
        print node
        
        if len(set(node['attr'] & set(attr)))>0:
            return
        else:
            for child in node['children']:
                downstream(chain,child,attr)
    
    downstream(chain,root,start)

#storing selection
sel=cmds.ls(selection=True)

points=cmds.ls(assemblies=True)

chains=[]
for p in points:
    
    shape=cmds.listRelatives(p,shapes=True,fullPath=True)
    if cmds.nodeType(shape)=='implicitBox':
        
        chains.append(traverse(p))

for c in chains:
    
    start=['IK_control','IK_solver_start']
    end=['IK_solver_end']
    
    print c
    breakdown(c,start=start,end=end)

#restoring selection
if sel:
    cmds.select(sel)
else:
    cmds.select(cl=True)