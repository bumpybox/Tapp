'''

- start attrs
- end attrs

'''

import maya.cmds as cmds

class TreeNode(object):
    def __init__(self, attr=None,name='',parent=None, children=[]):
        self.attr=attr
        self.name=name
        self.parent=parent
        self.children = list(children)

    def addChild(self, child):
        self.children.append(child)
    
    def getParent(self):
        return self.parent
    
    def downstream(self,searchAttr):
        if self.attr and len(set(self.attr) & set(searchAttr))>0:
            return self
        else:
            if self.children:
                for child in self.children:
                    return child.downstream(searchAttr)
            else:
                return None
    
    def getLast(self,root):
        result=[]
        
        if root.children:
            for child in root.children:
                result.extend(self.getLast(child))
        else:
            result=[root]
        
        return result

def buildTree(obj,parent=None):
    
    node=TreeNode()
    
    node.attr=cmds.listAttr(obj,userDefined=True)
    node.name=obj
    node.parent=parent
    
    children=cmds.listRelatives(obj,children=True,fullPath=True,type='transform')
    
    if children:
        for child in children:
            node.addChild(buildTree(child,parent=node))
        
        return node
    else:
        return node

tree=buildTree('|foot')
attr=['Spline_solver_end']
for last in tree.getLast(tree):
    print last.name

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