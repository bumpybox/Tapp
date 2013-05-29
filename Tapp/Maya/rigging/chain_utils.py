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

class TreeNode(object):
    def __init__(self, attr=None,name='',parent=None, children=[]):
        self.attr=attr
        self.name=name
        self.parent=parent
        self.children = list(children)

    def add(self, child):
        self.children.append(child)
    
    def getParent(self):
        return self.parent

def buildTree(obj,parent=None):
    
    node=TreeNode()
    
    node.attr=cmds.listAttr(obj,userDefined=True)
    node.name=obj
    node.parent=parent
    
    children=cmds.listRelatives(obj,children=True,fullPath=True,type='transform')
    
    if children:
        for child in children:
            node.add(buildTree(child,parent=node))
        
        return node
    else:
        return node

tree=buildTree('|foot')
print tree.children[0].getParent()

def breakdown(chain,start,end,root,resultChains=[]):
    
    endofchain=False
    
    def downstream(chain,node,attr,endofchain):
        
        if node['attr'] and len(set(node['attr']) & set(attr))>0:
            return node,endofchain
        else:
            if node['children']:
                for child in node['children']:
                    for n in chain:
                        if n['name']==child:
                            return downstream(chain,n,attr,endofchain)
            else:
                endofchain=True
                
                return node,endofchain
    
    startNode,endofchain=downstream(chain,root,start,endofchain)
    
    if endofchain==True:
        return resultChains
    
    for child in startNode['children']:
        for n in chain:
            if n['name']==child:
                startChild=n
    
    endNode,endofchain=downstream(chain,startChild,end,endofchain)
    
    def tween(chain,startNode,endNode,result=[]):
        
        result.append(startNode)
        
        if startNode['name']==endNode['name']:
            return result
        else:
            for child in startNode['children']:
                for n in chain:
                    if n['name']==child:
                        return tween(chain,n,endNode)
    
    tweenNodes=tween(chain,startNode,endNode)
    
    resultChains.append(tweenNodes)
    
    if tweenNodes[-1]['children']==None:
        return resultChains
    else:
        return breakdown(chain,start,end,tweenNodes[-1],resultChains=resultChains)

#storing selection
sel=cmds.ls(selection=True)

points=cmds.ls(assemblies=True)

chains=[]
for p in points:
    
    shape=cmds.listRelatives(p,shapes=True,fullPath=True)
    if cmds.nodeType(shape)=='implicitBox':
        
        chains.append(traverse(p))

for chain in chains:
    
    start=['FK_control','FK_solver_start']
    end=['FK_solver_end']
    
    bChains=breakdown(chain,start,end,chain[0])

#restoring selection
if sel:
    cmds.select(sel)
else:
    cmds.select(cl=True)