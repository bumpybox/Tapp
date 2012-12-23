import maya.cmds as cmds
import maya.mel as mel

class Math():
    ''' Class for all math related functions. '''
    
    def CrossProduct(self,posA,posB,posC):
        ''' Finds the up vector between three points in space.
        posA, posB and posC are points in space, passed in as
        a list. eg. posA=(x,y,z).
        Returns the vector.
        '''
        
        vectorA=[0,0,0]
        vectorB=[0,0,0]
        
        vectorA[0]=posA[0]-posB[0]
        vectorA[1]=posA[1]-posB[1]
        vectorA[2]=posA[2]-posB[2]
        
        vectorB[0]=posC[0]-posB[0]
        vectorB[1]=posC[1]-posB[1]
        vectorB[2]=posC[2]-posB[2]
        
        crs=mel.eval('crossProduct <<%s,%s,%s>> <<%s,%s,%s>> 1 1;'\
                        % (vectorA[0],vectorA[1],vectorA[2],
                           vectorB[0],vectorB[1],vectorB[2]))
        
        #return
        return crs

class ControlShape():
    ''' Class for all control shapes for rigging. '''
    
    def Square(self,name):
        ''' Creates a square shape. '''
        #creating the curve
        curve=cmds.curve(d=1, p=[(0,1,1),(0,1,-1),(0,-1,-1),
                                 (0,-1,1),(0,1,1)])
        
        #setup curve
        cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node
    
    def FourWay(self,name):
        ''' Creates a four leg arrow shape. '''
        
        #creating the curve
        curve=cmds.curve(d=1, p=[(-4, 0, 0),(-2, 0, -1.5),
                                 (-2, 0, -0.5),(-0.5, 0, -0.5),
                                 (-0.5, 0, -2),(-1.5, 0, -2),
                                 (0, 0, -4),(1.5, 0, -2),
                                 (0.5, 0, -2),(0.5, 0, -0.5),
                                 (2, 0, -0.5),(2, 0, -1.5),
                                 (4, 0, 0),(2, 0, 1.5),(2, 0, 0.5),
                                 (0.5, 0, 0.5),(0.5, 0, 2),
                                 (1.5, 0, 2),(0, 0, 4),
                                 (-1.5, 0, 2),(-0.5, 0, 2),
                                 (-0.5, 0, 0.5),(-2, 0, 0.5),
                                 (-2, 0, 1.5),(-4, 0, 0)])
        
        #resize to standard
        cmds.scale(0.25,0.25,0.25, curve)
        cmds.rotate(0,0,90,curve)
        
        cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node
    
    def Circle(self,name):
        ''' Creates a circle shape. '''
        
        #creating the curve
        curve=cmds.circle(radius=1,constructionHistory=False)
        
        #transform to standard
        cmds.rotate(0,90,0,curve)
        
        cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node
    
    def Box(self,name):
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
    
    def Pin(self,name):
        ''' Creates a pin shape. '''
        
        #creating the curve
        curve=cmds.curve(d=1,p=[(0,0,0),(0,1.2,0),
                                (-0.235114,1.276393,0),
                                (-0.380423,1.476393,0),
                                (-0.380423,1.723607,0),
                                (-0.235114,1.923607,0),(0,2,0),
                                (0.235114,1.923607,0),
                                (0.380423,1.723607,0),
                                (0.380423,1.476393,0),
                                (0.235114,1.276393,0),(0,1.2,0)])
        #transform to standard
        cmds.rotate(-90,-90,0,curve)
        
        cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node
    
    def Sphere(self,name):
        ''' Creates a sphere shape. '''
        
        #creating the curve
        curve=cmds.curve(d=1,p=[(0,1,0),(-0.382683,0.92388,0),
                                (-0.707107,0.707107,0),
                                (-0.92388,0.382683,0),(-1,0,0),
                                (-0.92388,-0.382683,0),
                                (-0.707107,-0.707107,0),
                                (-0.382683,-0.92388,0),(0,-1,0),
                                (0.382683,-0.92388,0),
                                (0.707107,-0.707107,0),
                                (0.92388,-0.382683,0),(1,0,0),
                                (0.92388,0.382683,0),
                                (0.707107,0.707107,0),
                                (0.382683,0.92388,0),(0,1,0),
                                (0,0.92388,0.382683),
                                (0,0.707107,0.707107),
                                (0,0.382683,0.92388),(0,0,1),
                                (0,-0.382683,0.92388),
                                (0,-0.707107,0.707107),
                                (0,-0.92388,0.382683),
                                (0,-1,0),(0,-0.92388,-0.382683),
                                (0,-0.707107,-0.707107),
                                (0,-0.382683,-0.92388),(0,0,-1),
                                (0,0.382683,-0.92388),
                                (0,0.707107,-0.707107),
                                (0,0.92388,-0.382683),(0,1,0),
                                (-0.382683,0.92388,0),
                                (-0.707107,0.707107,0),
                                (-0.92388,0.382683,0),(-1,0,0),
                                (-0.92388,0,0.382683),
                                (-0.707107,0,0.707107),
                                (-0.382683,0,0.92388),
                                (0,0,1),(0.382683,0,0.92388),
                                (0.707107,0,0.707107),
                                (0.92388,0,0.382683),(1,0,0),
                                (0.92388,0,-0.382683),
                                (0.707107,0,-0.707107),
                                (0.382683,0,-0.92388),
                                (0,0,-1),(-0.382683,0,-0.92388),
                                (-0.707107,0,-0.707107),
                                (-0.92388,0,-0.382683),(-1,0,0)])
        
        #naming control
        node=cmds.rename(curve,name)
        
        #return
        return node

class Transform():
    ''' Class for all transform related functions. '''
    
    def Snap(self,source,target,point=True,orient=True):
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
    
    def ChannelboxClean(self,node,attrs):
        ''' Removes list of attributes from the channelbox.
        Attributes are locked and unkeyable.
        '''
        
        for attr in attrs:
            cmds.setAttr('%s.%s' % (node,attr),lock=True,
                         keyable=False,channelBox=False)
    
    def ClosestOrient(self,source,target):
        ''' Returns degrees to rotate target to align closely to
        source. Degree steps are at 90, so visually orientation
        of target is preserved.
        source is node to align to.
        target is node to align.
        '''
        
        sourceRot=cmds.xform(source,q=True,ws=True,rotation=True)
        targetRot=cmds.xform(target,q=True,ws=True,rotation=True)
        
        xDiff=sourceRot[0]-targetRot[0]
        yDiff=sourceRot[1]-targetRot[1]
        zDiff=sourceRot[2]-targetRot[2]
        
        x=round((xDiff/90.0),0)*90.0
        y=round((yDiff/90.0),0)*90.0
        z=round((zDiff/90.0),0)*90.0
        
        return [x,y,z]