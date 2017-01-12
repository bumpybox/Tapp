import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om


def Distance(objA, objB):
    ''' Returns distance between two nodes. '''

    from math import sqrt, pow

    grp = cmds.group(empty=True)
    cmds.pointConstraint(objA, grp)
    At = cmds.xform(grp, ws=True, q=True, t=True)
    Ax = At[0]
    Ay = At[1]
    Az = At[2]
    cmds.delete(grp)

    grp = cmds.group(empty=True)
    cmds.pointConstraint(objB, grp)
    Bt = cmds.xform(grp, ws=True, q=True, t=True)
    Bx = Bt[0]
    By = Bt[1]
    Bz = Bt[2]
    cmds.delete(grp)

    return sqrt(pow(Ax - Bx, 2) + pow(Ay - By, 2) + pow(Az - Bz, 2))


def CrossProduct(posA,posB,posC):
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

def implicitSphere(name,group=False,size=1.0):
    ''' Creates a square shape.
        If group is True, will group control and
        return a list [group,control].
    '''
    
    #creating the curve
    curve=cmds.createNode('implicitSphere')
    curve=cmds.listRelatives(curve,parent=True)[0]
    
    #setup curve
    cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
    
    #naming control
    node=cmds.rename(curve,name)
    
    #sizing
    cmds.scale(size,size,size,node)
    cmds.FreezeTransformations(node)
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Square(name='square_cnt',group=False,size=1.0):
    ''' Creates a square shape.
        If group is True, will group control and
        return a list [group,control].
    '''
    
    #creating the curve
    curve=cmds.curve(d=1, p=[(0,1,1),(0,1,-1),(0,-1,-1),
                             (0,-1,1),(0,1,1)])
    
    #setup curve
    cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
    
    #naming control
    node=cmds.rename(curve,name)
    
    #sizing
    cmds.scale(size,size,size,node)
    cmds.FreezeTransformations(node)
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def FourWay(name='fourway_cnt',group=False,size=1.0):
    ''' Creates a four leg arrow shape.
        If group is True, will group control and
        return a list [group,control].
    '''
    
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
    
    #sizing
    cmds.scale(size,size,size,node)
    cmds.FreezeTransformations(node)
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Circle(name='circle_cnt',group=False,size=1.0):
    ''' Creates a circle shape.
        If group is True, will group control and
        return a list [group,control].
    '''
    
    #creating the curve
    curve=cmds.circle(radius=1,constructionHistory=False)
    
    #transform to standard
    cmds.rotate(0,90,0,curve)
    
    cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
    
    #naming control
    node=cmds.rename(curve,name)
    
    #sizing
    cmds.scale(size,size,size,node)
    cmds.FreezeTransformations(node)
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Box(name='box_cnt',group=False,size=1.0):
    ''' Creates a box shape.
        If group is True, will group control and
        return a list [group,control].
    '''
    
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
    
    #sizing
    cmds.scale(size,size,size,node)
    cmds.FreezeTransformations(node)
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Pin(name='pin_cnt',group=False,size=1.0):
    ''' Creates a pin shape.
        If group is True, will group control and
        return a list [group,control].
    '''
    
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
    cmds.rotate(0,-90,0,curve)
    
    cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
    
    #naming control
    node=cmds.rename(curve,name)
    
    #sizing
    cmds.scale(size,size,size,node)
    cmds.FreezeTransformations(node)
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Sphere(name='sphere_cnt',group=False,size=1.0):
    ''' Creates a sphere shape.
        If group is True, will group control and
        return a list [group,control].
    '''
    
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
    
    #sizing
    cmds.scale(size,size,size,node)
    cmds.FreezeTransformations(node)
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def icon(iconType=None,name=None,group=False,size=1.0):
    
    if iconType=='Square':
        if name:
            return Square(name=name,group=group, size=size)
        else:
            return Square(group=group, size=size)
    if iconType=='FourWay':
        if name:
            return FourWay(name=name,group=group, size=size)
        else:
            return FourWay(group=group, size=size)
    if iconType=='Circle':
        if name:
            return Circle(name=name,group=group, size=size)
        else:
            return Circle(group=group, size=size)
    if iconType=='Box':
        if name:
            return Box(name=name,group=group, size=size)
        else:
            return Box(group=group, size=size)
    if iconType=='Pin':
        if name:
            return Pin(name=name,group=group, size=size)
        else:
            return Pin(group=group, size=size)
    if iconType=='Sphere':
        if name:
            return Sphere(name=name,group=group, size=size)
        else:
            return Sphere(group=group, size=size)

def Snap(source,target,translation=True,rotation=True,scale=False):
    ''' Snaps target object to source object.
    If point is True, translation will snap.
    If orient is True, orientation will snap.
    If source is None, then it looks for lists for translation,rotation and scale
    '''
    
    #if source doesnt exists and passing in transform lists
    if not source:
        if isinstance(translation, list):
            cmds.xform(target,ws=True,translation=translation)
        if isinstance(rotation, list):
            cmds.xform(target,ws=True,rotation=rotation)
        if isinstance(scale, list):
            cmds.xform(target,scale=scale)
        
        return
    
    #translation
    if translation:
        trans=cmds.xform(source,q=True,ws=True,translation=True)
        cmds.xform(target,ws=True,translation=trans)
    
    #orientation
    if rotation:
        rot=cmds.xform(source,q=True,ws=True,rotation=True)
        cmds.xform(target,ws=True,rotation=rot)
    
    #scale
    if scale:
        scl=cmds.xform(source,q=True,r=True,scale=True)
        cmds.xform(target,scale=scl)

def GetWorldScale(node):
    ''' Gets scale in worldspace.
    
        Returns list [value,value,value]
    '''
    
    matrix=cmds.xform(node,q=True,ws=True,matrix=True)
    # create MMatrix from list
    mm = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(matrix,mm)
    # create MTransformationMatrix from MMatrix
    mt = om.MTransformationMatrix(mm)
    # for scale we need to utilize MScriptUtil to deal with the native
    # double pointers
    scaleUtil = om.MScriptUtil()
    scaleUtil.createFromList([0,0,0],3)
    scaleVec = scaleUtil.asDoublePtr()
    mt.getScale(scaleVec,om.MSpace.kWorld)
    
    scl = [om.MScriptUtil.getDoubleArrayItem(scaleVec,i) for i in range(0,3)]
    
    return scl

def RoundList(lst,digits):
    ''' Rounds a list of numbers '''
    
    newlist=[]
    for n in lst:
        newlist.append(round(n,digits))
    
    return newlist

def ChannelboxClean(node,attrs,lock=True,keyable=False):
    ''' Removes list of attributes from the channelbox.
    Attributes are locked and unkeyable.
    attrs is a list.
    '''
    
    for attr in attrs:
        cmds.setAttr('%s.%s' % (node,attr),lock=lock,
                     keyable=keyable,channelBox=False)

def ClosestOrient(source,target,align=True):
    ''' Rotates target to align closest to source, 
    while preserving visual orientation.
    source is node to align to.
    target is node to align.
    If align is false, returns the degrees to align.
    '''
    
    sourceRot=cmds.xform(source,q=True,ws=True,rotation=True)
    targetRot=cmds.xform(target,q=True,ws=True,rotation=True)
    
    xDiff=sourceRot[0]-targetRot[0]
    yDiff=sourceRot[1]-targetRot[1]
    zDiff=sourceRot[2]-targetRot[2]
    
    x=round((xDiff/90.0),0)*90.0
    y=round((yDiff/90.0),0)*90.0
    z=round((zDiff/90.0),0)*90.0
    
    if align==True:
        cmds.rotate(x,y,z,target,r=True,os=True)
    else:
        return [x,y,z]