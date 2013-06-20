class chain(object):
    '''
    Generic data handler. This is the basis from which everything is build.
    '''
    
    def __init__(self,node):
        
        if node:
            self.source=node
        
        self.name=''
        
        #tree data
        self.children=[]
        self.parent=None
        
        #transforms data
        self.translation=[]
        self.rotation=[]
        self.scale=[]
        
        #attribute data
        self.data=None
    
    def addChild(self,node):
        '''
        Will add the passed in node to the children list.
        '''
        self.children.append(node)
    
    def downstream(self,searchAttr):
        
        result=[]
        
        if self.children:
            for child in self.children:
                if child.data and len(set(child.data) & set(searchAttr))>0:
                    result=[child]
                else:
                    childData=child.downstream(searchAttr)
                    if childData:
                        result.extend(childData)
        else:
            return None,self
        
        return result
    
    def tween(self,endNode):
        
        result=[self]
        
        if self==endNode:
            return result
        
        if self.children:
            for child in self.children:
                result.extend(child.tween(endNode))
        
        return result
    
    def breakdown(self,startAttr,endAttr,result=[]):
        
        if len(set(self.data) & set(startAttr))>0:
            startNode=self
        else:
            startData=self.downstream(startAttr)
            if len(startData)>1:
                return result
            else:
                startNode=startData[0]
        
        endData=startNode.downstream(endAttr)
        if len(endData)>1:
            endNode=endData[1]
            
            result.append(startNode.tween(endNode))
            return result
        else:
            endNode=endData[0]
        
        result.append(startNode.tween(endNode))
        
        if endNode.children:
            return endNode.breakdown(startAttr,endAttr,result=result)
        
        return result