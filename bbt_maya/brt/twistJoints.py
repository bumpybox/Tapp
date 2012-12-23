import maya.cmds as cmds
import maya.mel as mel

from bbt_maya import generic
from bbt_maya.brt import utils

class TwistJoints():
    
    def rig(self,start,end,startMatrix,endMatrix,bendControl,
            attrControl,scaleRoot,amount,prefix):
        ''' Creates twist joints from start to end. '''
        
        #clear selection
        cmds.select(cl=True)
        
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
        ikHandle=cmds.ikHandle(sol='ikSplineSolver',
                               createCurve=True,
                               sj=jnts[0],endEffector=jnts[amount])
        
        cmds.setAttr(ikHandle[0]+'.dTwistControlEnable',1)
        cmds.setAttr(ikHandle[0]+'.dWorldUpType',4)
        
        cmds.connectAttr(startMatrix+'.worldMatrix[0]',
                         ikHandle[0]+'.dWorldUpMatrix',force=True)
        cmds.connectAttr(endMatrix+'.worldMatrix[0]',
                         ikHandle[0]+'.dWorldUpMatrixEnd',
                         force=True)
        
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
        
        nodes.append(bend01)
        nodes.append(bend01GRP)
        
        cmds.select(cl=True)
        pos=cmds.xform(ikHandle[2]+'.cv[2]',q=True,ws=True,
                       translation=True)
        bend02=cmds.joint(p=[0,0,0],n=prefix+'bend02_jnt')
        bend02GRP=cmds.group(bend02,n=prefix+'bend02_grp')
        cmds.xform(bend02GRP,ws=True,translation=pos)        
        ut.snap(start,bend02GRP,point=False)
        
        nodes.append(bend02)
        nodes.append(bend02GRP)
        
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
        
        ut.snap(bendControl,bend01GRP)
        ut.snap(bendControl,bend02GRP)
        
        cmds.parent(bend01GRP,bendControl)
        cmds.parent(bend02GRP,bendControl)
        
        bend01MD=cmds.shadingNode('multiplyDivide',asUtility=True,
                                  n=prefix+'bend01_md')
        bend02MD=cmds.shadingNode('multiplyDivide',asUtility=True,
                                  n=prefix+'bend02_md')
        bend01PMS=cmds.shadingNode('plusMinusAverage',
                                   asUtility=True,
                                   n=prefix+'bend01_pms')
        
        nodes.append(bend01MD)
        nodes.append(bend02MD)
        nodes.append(bend01PMS)
        
        cmds.setAttr(bend01MD+'.input2X',-dist)
        cmds.setAttr(bend02MD+'.input1Y',dist/1000)
        
        attrs=cmds.attributeInfo(attrControl,all=True)
        
        if 'bendy' not in attrs:
            cmds.addAttr(attrControl,longName='bendy'
                         ,attributeType='float',min=0,max=1,
                         keyable=True,)
        
        cmds.connectAttr(bend02MD+'.outputY',
                         bend01PMS+'.input1D[0]',force=True)
        cmds.connectAttr(attrControl+'.bendy',
                         bend01PMS+'.input1D[1]')
        cmds.connectAttr(bend01PMS+'.output1D',bend01MD+'.input1X')
        cmds.connectAttr(bend01MD+'.outputX',bend01+'.tx')
        cmds.connectAttr(bend01MD+'.outputX',bend02+'.tx')
        
        #making twist joints stretchy
        stretch01MD=cmds.shadingNode('multiplyDivide',
                                     asUtility=True,
                                         n=prefix+'stretch01MD')
        cmds.setAttr(stretch01MD+'.operation',2)
        cmds.setAttr(stretch01MD+'.input2X',dist)
        
        stretch02MD=cmds.shadingNode('multiplyDivide',
                                     asUtility=True,
                                         n=prefix+'stretch02MD')
        cmds.setAttr(stretch02MD+'.operation',2)
        cmds.connectAttr(scaleRoot+'.sx',stretch02MD+'.input2X')
        
        temp=cmds.listRelatives(ikHandle[2],s=True)
        temp1=cmds.arclen(temp[0],ch=True)
        stretchINFO=cmds.rename(temp1,prefix+'stretch_info')
        
        cmds.connectAttr(stretchINFO+'.arcLength',
                         stretch01MD+'.input1X',force=True)
        cmds.connectAttr(stretch01MD+'.outputX',
                         stretch02MD+'.input1X',force=True)
        
        for jnt in jnts:
            cmds.connectAttr(stretch02MD+'.outputX',jnt+'.sx')
        
        #making rig scalable
        cmds.parent(jnts[0],scaleRoot)
        
        #return
        return nodes