import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.utils.ZvParentMaster as muz

def SetWorld(childModule,worldModule,downStream=False):
    ''' Attaches all ik controls to world module. '''
    
    #getting world control
    worldcnt=mum.DownStream(worldModule, 'control')[0]
    worldcnt=mum.GetTransform(worldcnt)
    
    #getting all ik controls
    cnts=[]
    
    for cnt in mum.DownStream(childModule, 'control',allNodes=downStream):
        cnts.append(cnt)
    
    filterData={'system':'ik'}
    ikcnts=mum.Filter(cnts,filterData)
    
    #attaches ik control if they are prepped for ZvParentMaster
    for cnt in ikcnts:
        
        tn=mum.GetTransform(cnt)
        
        parent=cmds.listRelatives(tn,parent=True)[0]
        if parent.split('_')[-1]=='SN':
            cmds.select(tn,worldcnt,r=True)
            muz.attach()
            cmds.select(cl=True)

def Detach(module,detachChildren=False):
    
    #get child plug
    for plug in mum.DownStream(module, 'plug'):
        if len(mum.GetData(plug))<=3:
            childPlug=mum.GetTransform(plug)
    
    #detaching module
    cmds.select(childPlug,r=True)
    muz.detach()
    cmds.select(cl=True)
    
    parentModule=cmds.listConnections(module+'.metaParent',type='network')[0]
    
    cmds.disconnectAttr(parentModule+'.message',module+'.metaParent')
    
    #detaching children
    if detachChildren:
        
        for childModule in mum.DownStream(module, 'module'):
            Detach(childModule)

def Attach(childModule,parentModule):
    ''' Attaches child module to parent module. '''
    
    #get child plug
    for plug in mum.DownStream(childModule, 'plug'):
        if len(mum.GetData(plug))<=3:
            childPlug=mum.GetTransform(plug)
    
    #get closest socket
    sockets={}
    for socket in mum.DownStream(parentModule,'socket'):
        
        tn=mum.GetTransform(socket)
        sockets[tn]=Distance(tn, childPlug)
    
    parentSocket=min(sockets, key=sockets.get)
    
    #attaching plug to socket
    cmds.select(childPlug,parentSocket,r=True)
    muz.attach()
    cmds.select(cl=True)
    
    cmds.connectAttr(parentModule+'.message',childModule+'.metaParent',force=True)
    
    #scale constraining
    cmds.scaleConstraint(childPlug,parentSocket)

def Distance(objA,objB ):
    ''' Returns distance between two nodes. '''
    
    from math import sqrt,pow
    
    At=cmds.xform(objA,ws=True,q=True,t=True)
    Ax=At[0]
    Ay=At[1]
    Az=At[2]
    
    Bt=cmds.xform(objB,ws=True,q=True,t=True)
    Bx=Bt[0]
    By=Bt[1]
    Bz=Bt[2]
 
    return sqrt(  pow(Ax-Bx,2) + pow(Ay-By,2) + pow(Az-Bz,2)  )

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

def Square(name,group=False):
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
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def FourWay(name,group=False):
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
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Circle(name,group=False):
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
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Box(name,group=False):
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
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Pin(name,group=False):
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
    cmds.rotate(-90,-90,0,curve)
    
    cmds.makeIdentity(curve,apply=True, t=1, r=1, s=1, n=0)
    
    #naming control
    node=cmds.rename(curve,name)
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Sphere(name,group=False):
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
    
    #grouping control
    if group==True:
        grp=cmds.group(node,n=name+'_grp')
        
        return [grp,node]
    
    #return
    return node

def Snap(source,target,point=True,orient=True):
    ''' Snaps target object to source object.
    If point is True, translation will snap.
    If orient is True, orientation will snap.
    '''
    
    #translation
    if point==True:
        trans=cmds.xform(source,q=True,ws=True,translation=True)
        cmds.xform(target,ws=True,translation=trans)
    
    #orientation
    if orient==True:
        rot=cmds.xform(source,q=True,ws=True,rotation=True)
        cmds.xform(target,ws=True,rotation=rot)

def ChannelboxClean(node,attrs):
    ''' Removes list of attributes from the channelbox.
    Attributes are locked and unkeyable.
    attrs is a list.
    '''
    
    for attr in attrs:
        cmds.setAttr('%s.%s' % (node,attr),lock=True,
                     keyable=False,channelBox=False)

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