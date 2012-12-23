import maya.cmds as cmds
import maya.mel as mel

from bbt_maya import generic
from bbt_maya.brt import utils

class Foot():
    ''' Class for all foot related functions. '''
    
    def Create(self):
        pass
    
    def Import(self):
        pass
    
    def Rig(self,templateModule):
        #class variables
        meta=generic.Meta()
        ut=utils.Transform()
        ucs=utils.ControlShape()
        um=utils.Math()
        
        #collect all components
        controls=meta.DownStream(templateModule,'control',
                                 allNodes=True)
        
        for control in controls:
            data=meta.GetData(control)
            
            if data['component']=='foot':
                foot=meta.GetTransform(control)
            if data['component']=='toe':
                toe=meta.GetTransform(control)
            if data['component']=='toetip':
                toetip=meta.GetTransform(control)
            if data['component']=='heel':
                heel=meta.GetTransform(control)
            if data['component']=='bank' and data['side']=='right':
                rbank=meta.GetTransform(control)
            if data['component']=='bank' and data['side']=='left':
                lbank=meta.GetTransform(control)
        
        #getting transform data
        footTrans=cmds.xform(foot,worldSpace=True,query=True,
                              translation=True)
        toeTrans=cmds.xform(toe,worldSpace=True,query=True,
                              translation=True)
        toetipTrans=cmds.xform(toetip,worldSpace=True,query=True,
                              translation=True)
        heelTrans=cmds.xform(heel,worldSpace=True,query=True,
                              translation=True)
        heelRot=cmds.xform(heel,worldSpace=True,query=True,
                              rotation=True)
        rbankTrans=cmds.xform(rbank,worldSpace=True,query=True,
                              translation=True)
        rbankRot=cmds.xform(rbank,worldSpace=True,query=True,
                              rotation=True)
        lbankTrans=cmds.xform(lbank,worldSpace=True,query=True,
                              translation=True)
        lbankRot=cmds.xform(lbank,worldSpace=True,query=True,
                              rotation=True)
        
        #getting module data
        data=meta.GetData(templateModule)
        
        attachToLeg=data['attachToLeg']
        
        #establish side
        side='center'
        
        x=(footTrans[0]+toetipTrans[0]+heelTrans[0])/3
        
        if x>1.0:
            side='left'
        if x<-1.0:
            side='right'
        
        #establish index
        data=meta.GetData(templateModule)
        
        index=data['index']
        
        for node in cmds.ls(type='network'):
            data=meta.GetData(node)
            if 'index' in data.keys() and 'side' in data.keys()\
            and data['type']=='module' and data['side']==side and\
            data['index']==index:
                index+=1
        
        #delete template
        cmds.delete(cmds.listConnections('%s.message' % foot,
                                         type='dagContainer'))
        
        #establish prefix and suffix
        prefix=side[0]+'_'+'foot'+str(index)+'_'
        suffix='_'+side[0]+'_'+'foot'+str(index)
        
        #creating asset
        asset=cmds.container(n=prefix+'rig')
        
        #create module
        data={'side':side,'index':str(index)}
        
        module=meta.SetData(('meta'+suffix),'module','foot',None,
                            data)
        
        cmds.container(asset,e=True,addNode=module)
        
        #create joints
        footJNT=cmds.joint(position=(footTrans[0],footTrans[1],
                                        footTrans[2]),
                              name=prefix+'jnt01')
        toeJNT=cmds.joint(position=(toeTrans[0],toeTrans[1],
                                        toeTrans[2]),
                              name=prefix+'jnt02')
        
        cmds.container(asset,e=True,addNode=[footJNT,toeJNT])
        
        #create plug
        plug=cmds.spaceLocator(name=prefix+'plug')[0]
        
        cmds.xform(plug,worldSpace=True,translation=footTrans)
        
        metaParent=meta.SetData('meta_'+plug,'plug',None,module,
                                None)
        
        meta.SetTransform(plug, metaParent)
        
        cmds.container(asset,e=True,addNode=plug)
        
        #create sockets
        socket01=cmds.spaceLocator(name=prefix+'socket01')[0]
        socket02=cmds.spaceLocator(name=prefix+'socket02')[0]
        
        #setup sockets
        cmds.xform(socket01,worldSpace=True,translation=footTrans)
        cmds.xform(socket02,worldSpace=True,translation=toeTrans)
        
        cmds.parent(socket01,footJNT)
        cmds.parent(socket02,toeJNT)
        
        data={'index':1}
        metaParent=meta.SetData('meta_'+socket01,'socket',None,
                                module,data)
        meta.SetTransform(socket01, metaParent)
        data={'index':2}
        metaParent=meta.SetData('meta_'+socket02,'socket',None,
                                module,data)
        meta.SetTransform(socket02, metaParent)
        
        cmds.container(asset,e=True,addNode=[socket01,socket02])
        
        #finding the upVector for the joints
        crs=um.CrossProduct(footTrans,toeTrans,toetipTrans)
        
        #setup foot joint
        grp=cmds.group(empty=True)
        cmds.xform(grp,worldSpace=True,translation=footTrans)
        cmds.aimConstraint(toeJNT,grp,worldUpType='vector',
                           worldUpVector=crs)
        
        rot=cmds.xform(grp,query=True,rotation=True)
        cmds.rotate(rot[0],rot[1],rot[2],footJNT,
                    worldSpace=True,pcp=True)
        
        cmds.makeIdentity(footJNT,apply=True,t=1,r=1,s=1,n=0)
        
        cmds.delete(grp)
        
        cmds.parent(footJNT,plug)
        
        #setup toe joint
        grp=cmds.group(empty=True)
        temp=cmds.group(empty=True)
        cmds.xform(grp,worldSpace=True,translation=toeTrans)
        cmds.xform(temp,worldSpace=True,translation=toetipTrans)
        cmds.aimConstraint(temp,grp,worldUpType='vector',
                           worldUpVector=crs)
        
        rot=cmds.xform(grp,query=True,rotation=True)
        cmds.rotate(rot[0],rot[1],rot[2],toeJNT,worldSpace=True,
                    pcp=True)
        
        cmds.delete(grp)
        cmds.delete(temp)
        
        cmds.makeIdentity(toeJNT,apply=True, t=1, r=1, s=1, n=0)
        
        #create ik chain
        footIK=cmds.duplicate(footJNT,st=True,po=True,
                               n=prefix+'ik01')[0]
        toeIK=cmds.duplicate(toeJNT,st=True,po=True,
                               n=prefix+'ik02')[0]
        
        cmds.container(asset,e=True,addNode=[footIK,toeIK])
        
        #setup ik chain
        cmds.parent(toeIK,footIK)
        
        cmds.connectAttr('%s.scale' % footIK,
                         '%s.inverseScale' % toeIK,force=True)
        
        #create fk chain
        footFK=cmds.duplicate(footJNT,st=True,po=True,
                               n=prefix+'fk01')[0]
        toeFK=cmds.duplicate(toeJNT,st=True,po=True,
                               n=prefix+'fk02')[0]
        
        cmds.container(asset,e=True,addNode=[footFK,toeFK])
        
        #setup fk chain
        cmds.parent(toeFK,footFK)
        
        cmds.connectAttr('%s.scale' % footFK,
                         '%s.inverseScale' % toeFK,force=True)
        
        #create controls
        zeroCNT=cmds.createNode('transform',ss=True,
                                n=prefix+'zero_cnt')
        
        ballCNT=ucs.Circle(prefix+'ball_cnt')
        toeIkCNT=ucs.Circle(prefix+'toeIk_cnt')
        toetipCNT=ucs.Sphere(prefix+'toetip_cnt')
        heelCNT=ucs.Sphere(prefix+'heel_cnt')
        footCNT=ucs.Sphere(prefix+'foot_cnt')
        toeFkCNT=ucs.Square(prefix+'toeFk_cnt')
        
        cmds.container(asset,e=True,addNode=[ballCNT,toeIkCNT,
                                             toetipCNT,heelCNT,
                                             footCNT,toeFkCNT])
        
        #setup ballCNT
        data={'system':'ik','switch':zeroCNT}
        mNode=meta.SetData(('meta_'+ballCNT),'control','ball',
                           module,data)
        meta.SetTransform(ballCNT, mNode)
        
        cmds.scale(1.5,1.5,1.5,ballCNT)
        cmds.makeIdentity(ballCNT,apply=True, t=1, r=1, s=1, n=0)
        
        grp=cmds.group(ballCNT,n=(ballCNT+'_grp'))
        cmds.parent(grp,plug)
        
        ut.Snap(toeJNT,grp)
        
        cmds.container(asset,e=True,addNode=[grp])
        
        #setup toeIkCNT
        data={'system':'ik','switch':toeFK}
        mNode=meta.SetData(('meta_'+toeIkCNT),'control','toe',
                           module,data)
        meta.SetTransform(toeIkCNT, mNode)
        
        grp=cmds.group(toeIkCNT,n=(toeIkCNT+'_grp'))
        cmds.parent(grp,plug)
        
        ut.Snap(toeJNT,grp)
        
        cmds.container(asset,e=True,addNode=[grp])
        
        #setup toetipCNT
        data={'system':'ik','switch':zeroCNT}
        mNode=meta.SetData(('meta_'+toetipCNT),'control','toetip',
                           module,data)
        meta.SetTransform(toetipCNT, mNode)
        
        grp=cmds.group(toetipCNT,n=(toetipCNT+'_grp'))
        cmds.parent(grp,plug)
        
        cmds.xform(grp,ws=True,rotation=heelRot)
        cmds.xform(grp,ws=True,translation=toetipTrans)
        
        cmds.container(asset,e=True,addNode=[grp])
        
        #setup heelCNT
        data={'system':'ik','switch':zeroCNT}
        mNode=meta.SetData(('meta_'+heelCNT),'control','heel',
                           module,data)
        meta.SetTransform(heelCNT, mNode)
        
        grp=cmds.group(heelCNT,n=(heelCNT+'_grp'))
        cmds.parent(grp,plug)
        
        cmds.xform(grp,ws=True,rotation=heelRot)
        cmds.xform(grp,ws=True,translation=heelTrans)
        
        cmds.container(asset,e=True,addNode=[grp])
        
        #setup footCNT
        data={'system':'ik','switch':zeroCNT}
        mNode=meta.SetData(('meta_'+footCNT),'control','foot',
                           module,data)
        meta.SetTransform(footCNT, mNode)
        
        grp=cmds.group(footCNT,n=(footCNT+'_grp'))
        cmds.parent(grp,plug)
        
        cmds.xform(grp,ws=True,rotation=heelRot)
        cmds.xform(grp,ws=True,translation=heelTrans)
        cmds.move(0,0,-2,grp,r=True,os=True)
        
        cmds.container(asset,e=True,addNode=[grp])
        
        #setup toeFkCNT
        data={'system':'fk','switch':toeIK}
        mNode=meta.SetData(('meta_'+toeFkCNT),'control','toe',
                           module,data)
        meta.SetTransform(toeFkCNT, mNode)
        
        grp=cmds.group(toeFkCNT,n=(toeFkCNT+'_grp'))
        cmds.parent(grp,plug)
        
        ut.Snap(toeJNT,grp)
        
        cmds.container(asset,e=True,addNode=[grp])
        
        #continue with 'setup foot controls'

templateModule='meta_foot'

foot=Foot()
foot.Rig(templateModule)