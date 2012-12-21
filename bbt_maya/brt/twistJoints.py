import maya.cmds as cmds
import maya.mel as mel

from bbt_maya import generic
from bbt_maya.brt import utils

class TwistJoints():
    
    def rig(self,start,end,startMatrix,endMatrix,bendControl,
            amount,prefix):
        ''' Creates twist joints from start to end. '''
        
        #nodes collection
        nodes=[]
        
        #calculate distance
        startPOS=cmds.xform(start,q=True,translation=True,ws=True)
        endPOS=cmds.xform(end,q=True,translation=True,ws=True)
        
        distX=startPOS[0]-endPOS[0]
        distY=startPOS[1]-endPOS[1]
        distZ=startPOS[2]-endPOS[2]
        
        dist=mel.eval('mag <<%s,%s,%s>>;' % (distX,distY,distZ))
        
        #create joints
        jnts=[]
        
        for count in xrange(0,amount+1):
            jnt=cmds.joint(p=((dist/amount)*count,0,0),
                           n=prefix+'twist'+str(count))
            
            jnts.append(jnt)
            nodes.append(jnt)
        
        ut=utils.transform()
        ut.snap(start, jnts[0])
        
        #setup joints
        ikHandle=cmds.ikHandle(sol='ikSplineSolver',createCurve=True
                      ,sj=jnts[0],endEffector=jnts[amount])
        
        cmds.setAttr(ikHandle[0]+'.dTwistControlEnable',1)
        cmds.setAttr(ikHandle[0]+'.dWorldUpType',4)
        
        cmds.connectAttr(startMatrix+'.worldMatrix[0]',
                         ikHandle[0]+'.dWorldUpMatrix',force=True)
        cmds.connectAttr(endMatrix+'.worldMatrix[0]',
                         ikHandle[0]+'.dWorldUpMatrixEnd',force=True)
        
        nodes.append(ikHandle[0])
        nodes.append(ikHandle[1])
        nodes.append(ikHandle[2])
        
        #create bend joints
        cmds.select(cl=True)
        pos=cmds.xform(ikHandle[2]+'.cv[1]',q=True,ws=True,
                       translation=True)
        bend01=cmds.joint(p=[0,0,0],n=prefix+'bend01_jnt')
        bend01GRP=cmds.group(bend01,n=prefix+'bend01_grp')
        cmds.xform(bend01GRP,ws=True,translation=pos)        
        ut.snap(start,bend01GRP,point=False)
        
        cmds.select(cl=True)
        pos=cmds.xform(ikHandle[2]+'.cv[2]',q=True,ws=True,
                       translation=True)
        bend02=cmds.joint(p=[0,0,0],n=prefix+'bend02_jnt')
        bend02GRP=cmds.group(bend02,n=prefix+'bend02_grp')
        cmds.xform(bend02GRP,ws=True,translation=pos)        
        ut.snap(start,bend02GRP,point=False)
        
        #setup bend joints
        skin=cmds.skinCluster(start,bend01,bend02,ikHandle[2])[0]
        
        cmds.skinPercent(skin,ikHandle[2]+'.cv[0]',
                         transformValue=[(start, 1)])
        cmds.skinPercent(skin,ikHandle[2]+'.cv[1]',
                         transformValue=[(bend01, 1)])
        cmds.skinPercent(skin,ikHandle[2]+'.cv[2]',
                         transformValue=[(bend02, 1)])
        cmds.skinPercent(skin,ikHandle[2]+'.cv[3]',
                         transformValue=[(start, 1)])
        
        ut.snap(bendControl,bend01GRP,orient=False)
        ut.snap(bendControl,bend02GRP,orient=False)
        
        cmds.parent(bend01GRP,bendControl)
        cmds.parent(bend02GRP,bendControl)
        
        #continue with bendy network setup
        
        #return
        return nodes

tj=TwistJoints()
tj.rig('l_arm1_jnt01', 'l_arm1_average_jnt','l_arm1_plug'
       ,'l_arm1_jnt02','l_arm1_average_jnt', 3,'somthing')