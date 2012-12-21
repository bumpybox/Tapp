import maya.cmds as cmds

class controlShape():
    ''' Class for all control shapes for rigging. '''
    
    def fourWay(self,name):
        ''' Creates a four leg arrow shape. '''
        
        #creating the curve
        curve=cmds.curve(d=1, p=[(-4, 0, 0),(-2, 0, -1.5),(-2, 0, -0.5),
                           (-0.5, 0, -0.5),(-0.5, 0, -2),(-1.5, 0, -2),
                           (0, 0, -4),(1.5, 0, -2),(0.5, 0, -2),
                           (0.5, 0, -0.5),(2, 0, -0.5),(2, 0, -1.5),
                           (4, 0, 0),(2, 0, 1.5),(2, 0, 0.5),
                           (0.5, 0, 0.5),(0.5, 0, 2),(1.5, 0, 2),
                           (0, 0, 4),(-1.5, 0, 2),(-0.5, 0, 2),
                           (-0.5, 0, 0.5),(-2, 0, 0.5),(-2, 0, 1.5),(-4, 0, 0)])
        
        #resize to standard
        cmds.scale(0.25,0.25,0.25, curve)
        
        cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node
    
    def circle(self,name):
        ''' Creates a circle shape. '''
        
        #creating the curve
        curve=cmds.circle(radius=1,constructionHistory=False)
        
        #transform to standard
        cmds.rotate(90,0,0,curve)
        
        cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node
    
    def box(self,name):
        ''' Creates a box shape. '''
        
        #creating the curve
        curve=cmds.curve(d=1, p=[(1,1,-1),(1,1,1),(1,-1,1),
                                 (1,-1,-1),(1,1,-1),(-1,1,-1),
                                 (-1,-1,-1),(-1,-1,1),(-1,1,1),
                                 (1,1,1),(1,-1,1),(-1,-1,1),
                                 (-1,-1,-1),(1,-1,-1),(1,1,-1),
                                 (-1,1,-1),(-1,1,1),(1,1,1),
                                 (1,1,-1)])
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node
    
    def pin(self,name):
        ''' Creates a pin shape. '''
        
        #creating the curve
        curve=cmds.curve(d=1,p=[(0,0,0),(0,1.2,0),(-0.235114,1.276393,0),
                                (-0.380423,1.476393,0),(-0.380423,1.723607,0),
                                (-0.235114,1.923607,0),(0,2,0),(0.235114,1.923607,0),
                                (0.380423,1.723607,0),(0.380423,1.476393,0),
                                (0.235114,1.276393,0),(0,1.2,0)])
        #transform to standard
        cmds.rotate(-90,-90,0,curve)
        
        cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node
    
    def sphere(self,name):
        ''' Creates a sphere shape. '''
        
        #creating the curve
        curve=cmds.curve(d=1,p=[(0,1,0),(-0.382683,0.92388,0),(-0.707107,0.707107,0),
                                (-0.92388,0.382683,0),(-1,0,0),(-0.92388,-0.382683,0),
                                (-0.707107,-0.707107,0),(-0.382683,-0.92388,0),(0,-1,0),
                                (0.382683,-0.92388,0),(0.707107,-0.707107,0),
                                (0.92388,-0.382683,0),(1,0,0),(0.92388,0.382683,0),
                                (0.707107,0.707107,0),(0.382683,0.92388,0),(0,1,0),
                                (0,0.92388,0.382683),(0,0.707107,0.707107),
                                (0,0.382683,0.92388),(0,0,1),(0,-0.382683,0.92388),
                                (0,-0.707107,0.707107),(0,-0.92388,0.382683),
                                (0,-1,0),(0,-0.92388,-0.382683),(0,-0.707107,-0.707107),
                                (0,-0.382683,-0.92388),(0,0,-1),(0,0.382683,-0.92388),
                                (0,0.707107,-0.707107),(0,0.92388,-0.382683),(0,1,0),
                                (-0.382683,0.92388,0),(-0.707107,0.707107,0),
                                (-0.92388,0.382683,0),(-1,0,0),(-0.92388,0,0.382683),
                                (-0.707107,0,0.707107),(-0.382683,0,0.92388),
                                (0,0,1),(0.382683,0,0.92388),(0.707107,0,0.707107),
                                (0.92388,0,0.382683),(1,0,0),(0.92388,0,-0.382683),
                                (0.707107,0,-0.707107),(0.382683,0,-0.92388),
                                (0,0,-1),(-0.382683,0,-0.92388),(-0.707107,0,-0.707107),
                                (-0.92388,0,-0.382683),(-1,0,0)])
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node

class transform():
    ''' Class for all transform related functions. '''
    
    def snap(self,source,target,point=True,orient=True):
        ''' Snaps source object to target object.
        If point is True, translation will snap.
        If orient is True, orientation will snap.
        '''
        
        #translation
        if point==True:
            cmds.delete(cmds.pointConstraint(source,target))
        
        #orientation
        if orient==True:
            cmds.delete(cmds.orientConstraint(source,target))
    
    def channelboxClean(self,node,attrs):
        ''' Removes list of attributes from the channelbox.
        Attributes are locked and unkeyable.
        '''
        
        for attr in attrs:
            cmds.setAttr('%s.%s' % (node,attr),lock=True,keyable=False,channelBox=False)