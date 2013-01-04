import maya.cmds as cmds
import maya.mel as mel

from bbt_maya import generic
from bbt_maya.brt.modules import utils
from bbt_maya.python import ZvParentMaster as zv

class Spine():
    ''' Class for all limb related functions. '''
    
    def Create(self):
        pass
    
    def Import(self):
        pass
    
    def Attach(self,sourceModule,targetModule):
        pass
    
    def Detach(self,module):
        pass
    
    def Rig(self,module):
        ''' Rigs the provided module. '''
        
        #class variables
        meta=generic.Meta()
        ut=utils.Transform()
        ucs=utils.ControlShape()
        um=utils.Math()
        
        #collect all components
        controls=meta.DownStream(module,'control')
        
        for control in controls:
            if meta.GetData(control)['component']=='start':
                start=meta.GetTransform(control)
            if meta.GetData(control)['component']=='line':
                line=meta.GetTransform(control)
            if meta.GetData(control)['component']=='end':
                end=meta.GetTransform(control)
        
        #getting module data
        data=meta.GetData(module)
        
        jointAmount=data['joints']
        hipsAttach=data['hips']
        
        #getting transform data
        startTrans=cmds.xform(start,worldSpace=True,query=True,
                              translation=True)
        startRot=cmds.xform(start,worldSpace=True,query=True,
                          rotation=True)
        endTrans=cmds.xform(end,worldSpace=True,query=True,
                            translation=True)
        endRot=cmds.xform(end,worldSpace=True,query=True,
                          rotation=True)
        
        jntsTrans=[]
        
        grp=cmds.group(empty=True)
        path=cmds.pathAnimation(grp,follow=True,c=line)
        
        for count in xrange(0,jointAmount+1):
            pct=1.0/jointAmount*count
            
            cmds.setAttr(path+'.uValue',pct)
            
            trans=cmds.xform(grp,q=True,ws=True,translation=True)
            jntsTrans.append(trans)
        
        cmds.delete(grp,path)
        
        #establish side
        side='center'
        
        x=(startTrans[0]+endTrans[0])/2
        
        if x>1.0:
            side='left'
        if x<-1.0:
            side='right'
        
        #establish index
        data=meta.GetData(module)
        
        index=data['index']
        
        for node in cmds.ls(type='network'):
            data=meta.GetData(node)
            if 'index' in data.keys() and \
            'side' in data.keys() and \
            'component' in data.keys() and \
            data['type']=='module' and \
            data['side']==side and \
            data['index']==index:
                index+=1
        
        #delete template
        cmds.delete(cmds.container(q=True,fc=start))
        
        #establish prefix and suffix
        prefix=side[0]+'_'+'spine'+str(index)+'_'
        suffix='_'+side[0]+'_'+'spine'+str(index)
        
        #creating asset
        asset=cmds.container(n=prefix+'rig')
        
        #create module
        data={'side':side,'index':str(index),'system':'rig'}
        
        module=meta.SetData(('meta'+suffix),'module','spine',None,
                            data)
        
        cmds.container(asset,e=True,addNode=module)
        
        #create plug
        plug=cmds.spaceLocator(name=prefix+'plug')[0]
        
        phgrp=cmds.group(plug,n=(plug+'_PH'))
        sngrp=cmds.group(plug,n=(plug+'_SN'))
        
        cmds.xform(phgrp,worldSpace=True,translation=startTrans)
        
        metaParent=meta.SetData('meta_'+plug,'plug',None,module,
                                None)
        
        meta.SetTransform(plug, metaParent)
        
        cmds.container(asset,e=True,addNode=[plug,phgrp,sngrp])
        
        #create fkjnts, ikjnts, jnts, sockets, fkcnts
        fkcnts=[]
        fkcntsGRP=[]
        fkjnts=[]
        ikjnts=[]
        jnts=[]
        sockets=[]
        
        for pos in jntsTrans:
            
            count=jntsTrans.index(pos)+1
            
            #create joints
            jnt=cmds.joint(position=(pos[0],pos[1],pos[2]),
                                  name=prefix+'jnt'+str(count))
            
            cmds.container(asset,e=True,addNode=jnt)
            
            if len(jnts)>0:
                cmds.parent(jnt,jnts[-1])
            
            jnts.append(jnt)
            
            if len(jnts)<jointAmount+1:
                grp=cmds.group(empty=True)
                newPos=jntsTrans[count]
                cmds.xform(grp,worldSpace=True,
                           translation=newPos)
                aimCon=cmds.aimConstraint(grp,jnt,
                                          worldUpVector=(1,0,0))
                cmds.delete(aimCon)
                
                cmds.makeIdentity(jnt,apply=True,t=1,r=1,s=1,n=0)
                
                cmds.delete(grp)
            else:
                ut.Snap(jnts[-2],jnt,point=False)
            
            #create sockets
            socket=cmds.spaceLocator(name=prefix+'socket'+
                                     str(count))[0]
            
            ut.Snap(jnt,socket)
            cmds.parent(socket,jnt)
            
            data={'index':count}
            metaParent=meta.SetData('meta_'+socket,'socket',None,
                                    module,data)
            meta.SetTransform(socket, metaParent)
            
            sockets.append(socket)
            
            cmds.container(asset,e=True,addNode=socket)
            
            #create fk
            cmds.select(cl=True)
            fk=cmds.joint(position=(pos[0],pos[1],pos[2]),
                                  name=prefix+'fk'+str(count))
            
            ut.Snap(jnt,fk)
            cmds.makeIdentity(fk,apply=True,t=1,r=1,s=1,n=0)
            
            cmds.container(asset,e=True,addNode=fk)
            
            #create fk controls
            [grp,cnt]=ucs.Square(prefix+'fk'+str(count)+'_cnt',
                           group=True)
            
            cmds.container(asset,e=True,addNode=[grp,cnt])
            
            fkcnts.append(cnt)
            fkcntsGRP.append(grp)
            
            #setup fk controls
            ut.Snap(fk,grp)
            
            cmds.parent(fk,cnt)
            
            if len(fkjnts)>0:
                cmds.parent(grp,fkjnts[-1])
            
            fkjnts.append(fk)
            
            #create ik
            cmds.select(cl=True)
            ik=cmds.joint(position=(pos[0],pos[1],pos[2]),
                                  name=prefix+'ik'+str(count))
            
            ut.Snap(jnt,ik)
            cmds.makeIdentity(ik,apply=True,t=1,r=1,s=1,n=0)
            
            cmds.container(asset,e=True,addNode=ik)
            
            #setup ik
            if len(ikjnts)>0:
                cmds.parent(ik,ikjnts[-1])
            
            ikjnts.append(ik)
            
        
        cmds.parent(jnts[0],plug)
        cmds.parent(fkcntsGRP[0],plug)
        
        #create end joint
        chestJNT=cmds.duplicate(jnts[-1],st=True,po=True,
                                n=prefix+'end_jnt')[0]
        
        cmds.container(asset,e=True,addNode=chestJNT)
        
        #setup chest joint
        cmds.parent(sockets[-1],chestJNT)
        
        #create controls
        [masterGRP,masterCNT]=ucs.FourWay(prefix+'master_cnt',
                                        group=True)
        [endGRP,endCNT]=ucs.Sphere(prefix+'end_cnt',group=True)
        [startGRP,startCNT]=ucs.Sphere(prefix+'start_cnt',
                                       group=True)
        [midGRP,midCNT]=ucs.Sphere(prefix+'mid_cnt',group=True)
        
        cnts=[masterCNT,endCNT,startCNT,midCNT]
        cntsGRP=[masterGRP,endGRP,startGRP,midGRP]
        
        cmds.container(asset,e=True,addNode=cnts)
        cmds.container(asset,e=True,addNode=cntsGRP)
        
        #setup master control
        cmds.xform(masterGRP,ws=True,translation=startTrans)
        cmds.xform(masterGRP,ws=True,rotation=startRot)
        
        ut.ClosestOrient(jnts[0], masterGRP, align=True)
        
        #setup start control
        cmds.xform(startGRP,ws=True,translation=startTrans)
        cmds.xform(startGRP,ws=True,rotation=startRot)
        
        ut.ClosestOrient(jnts[0], startGRP, align=True)
        
        #setup end control
        cmds.xform(endGRP,ws=True,translation=endTrans)
        cmds.xform(endGRP,ws=True,rotation=endRot)
        
        ut.ClosestOrient(startGRP,endGRP, align=True)
        
        #setup mid control
        cmds.delete(cmds.parentConstraint(startGRP,endGRP,midGRP))
        
        

templateModule='meta_spine'

spine=Spine()
spine.Rig(templateModule)