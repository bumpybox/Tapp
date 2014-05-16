import maya.cmds as cmds

def setupAttrs(prefix,cnt):
    cmds.setAttr('%s.tz' % cnt,lock=True,keyable=False,channelBox=False)
    cmds.setAttr('%s.rx' % cnt,lock=True,keyable=False,channelBox=False)
    cmds.setAttr('%s.ry' % cnt,lock=True,keyable=False,channelBox=False)
    cmds.setAttr('%s.rz' % cnt,lock=True,keyable=False,channelBox=False)
    cmds.setAttr('%s.sx' % cnt,lock=True,keyable=False,channelBox=False)
    cmds.setAttr('%s.sy' % cnt,lock=True,keyable=False,channelBox=False)
    cmds.setAttr('%s.sz' % cnt,lock=True,keyable=False,channelBox=False)
    cmds.setAttr('%s.v' % cnt,lock=True,keyable=False,channelBox=False)
    
    cmds.addAttr(cnt,longName='N',at='float')
    cmds.setAttr('%s.N' % cnt,keyable=True)
    cmds.addAttr(cnt,longName='S',at='float')
    cmds.setAttr('%s.S' % cnt,keyable=True)
    cmds.addAttr(cnt,longName='E',at='float')
    cmds.setAttr('%s.E' % cnt,keyable=True)
    cmds.addAttr(cnt,longName='W',at='float')
    cmds.setAttr('%s.W' % cnt,keyable=True)
    cmds.addAttr(cnt,longName='NE',at='float')
    cmds.setAttr('%s.NE' % cnt,keyable=True)
    cmds.addAttr(cnt,longName='NW',at='float')
    cmds.setAttr('%s.NW' % cnt,keyable=True)
    cmds.addAttr(cnt,longName='SE',at='float')
    cmds.setAttr('%s.SE' % cnt,keyable=True)
    cmds.addAttr(cnt,longName='SW',at='float')
    cmds.setAttr('%s.SW' % cnt,keyable=True)
    
    nCLP=cmds.shadingNode('clamp',asUtility=True,name=(prefix+'_N_clp'))
    cmds.setAttr('%s.maxR' % nCLP,1)
    eCLP=cmds.shadingNode('clamp',asUtility=True,name=(prefix+'_E_clp'))
    cmds.setAttr('%s.maxR' % eCLP,1)
    sCLP=cmds.shadingNode('clamp',asUtility=True,name=(prefix+'_S_clp'))
    cmds.setAttr('%s.minR' % sCLP,-1)
    sMD=cmds.shadingNode('multiplyDivide',asUtility=True,name=(prefix+'_S_md'))
    cmds.setAttr('%s.input2X' % sMD,-1)
    wCLP=cmds.shadingNode('clamp',asUtility=True,name=(prefix+'_W_clp'))
    cmds.setAttr('%s.minR' % wCLP,-1)
    wMD=cmds.shadingNode('multiplyDivide',asUtility=True,name=(prefix+'_W_md'))
    cmds.setAttr('%s.input2X' % wMD,-1)
    neMD=cmds.shadingNode('multiplyDivide',asUtility=True,name=(prefix+'_NE_md'))
    nwMD=cmds.shadingNode('multiplyDivide',asUtility=True,name=(prefix+'_NW_md'))
    seMD=cmds.shadingNode('multiplyDivide',asUtility=True,name=(prefix+'_SE_md'))
    swMD=cmds.shadingNode('multiplyDivide',asUtility=True,name=(prefix+'_SW_md'))
    
    cmds.connectAttr('%s.ty' % cnt,'%s.inputR' % nCLP)
    cmds.connectAttr('%s.outputR' % nCLP,'%s.N' % cnt)
    
    cmds.connectAttr('%s.tx' % cnt,'%s.inputR' % eCLP)
    cmds.connectAttr('%s.outputR' % eCLP,'%s.E' % cnt)
    
    cmds.connectAttr('%s.ty' % cnt,'%s.inputR' % sCLP)
    cmds.connectAttr('%s.outputR' % sCLP,'%s.input1X' % sMD)
    cmds.connectAttr('%s.outputX' % sMD,'%s.S' % cnt)
    
    cmds.connectAttr('%s.tx' % cnt,'%s.inputR' % wCLP)
    cmds.connectAttr('%s.outputR' % wCLP,'%s.input1X' % wMD)
    cmds.connectAttr('%s.outputX' % wMD,'%s.W' % cnt)
    
    cmds.connectAttr('%s.N' % cnt,'%s.input1X' % neMD)
    cmds.connectAttr('%s.E' % cnt,'%s.input2X' % neMD)
    cmds.connectAttr('%s.outputX' % neMD,'%s.NE' % cnt)
    
    cmds.connectAttr('%s.N' % cnt,'%s.input1X' % nwMD)
    cmds.connectAttr('%s.W' % cnt,'%s.input2X' % nwMD)
    cmds.connectAttr('%s.outputX' % nwMD,'%s.NW' % cnt)
    
    cmds.connectAttr('%s.S' % cnt,'%s.input1X' % seMD)
    cmds.connectAttr('%s.E' % cnt,'%s.input2X' % seMD)
    cmds.connectAttr('%s.outputX' % seMD,'%s.SE' % cnt)
    
    cmds.connectAttr('%s.S' % cnt,'%s.input1X' % swMD)
    cmds.connectAttr('%s.W' % cnt,'%s.input2X' % swMD)
    cmds.connectAttr('%s.outputX' % swMD,'%s.SW' % cnt)

def sliderA(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(-1,0,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(-1,0,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(0,-1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(1,0,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(0,1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(-1,1),etx=(1,1))
    cmds.transformLimits(cnt,ty=(-1,1),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderB_north(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(-1,0,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(-1,0,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(1,1,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(0,1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(-1,1),etx=(1,1))
    cmds.transformLimits(cnt,ty=(0,1),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderB_east(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(0,0,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(1,-1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(1,0,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(0,1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(0,1),etx=(1,1))
    cmds.transformLimits(cnt,ty=(-1,1),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderB_south(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(-1,-1,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(-1,-1,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(0,-1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(1,0,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(-1,1),etx=(1,1))
    cmds.transformLimits(cnt,ty=(-1,0),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderB_west(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(-1,0,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(-1,0,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(0,-1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(-1,1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(-1,0),etx=(1,1))
    cmds.transformLimits(cnt,ty=(-1,1),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderC_vertical(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(0,0,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(1,-1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(-1,1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,ty=(-1,1),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderC_north(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(0,0,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(1,1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(0,1,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(-1,1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,ty=(0,1),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderC_south(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(0,-1,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(0,-1,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(1,-1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(-1,-1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,ty=(-1,0),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderC_horizontal(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(-1,-1,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(-1,-1,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(1,1,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(-1,1),etx=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderC_east(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(0,-1,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(0,-1,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(1,0,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(1,1,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(0,1),etx=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderC_west(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(-1,-1,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(-1,-1,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(-1,1,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(-1,0,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(-1,0),etx=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderD_northeast(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(0,0,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(1,0,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(1,1,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(0,1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(0,1),etx=(1,1))
    cmds.transformLimits(cnt,ty=(0,1),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderD_northwest(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(-1,0,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(-1,0,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(0,1,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(-1,1,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(-1,0),etx=(1,1))
    cmds.transformLimits(cnt,ty=(0,1),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderD_southeast(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(0,-1,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(0,-1,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(1,-1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(1,0,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(0,1),etx=(1,1))
    cmds.transformLimits(cnt,ty=(-1,0),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)

def sliderD_southwest(prefix):
    cmds.undoInfo(openChunk=True)
    
    #create nodes
    grp=cmds.group(empty=True,n=(prefix+'_grp'))
    cnt=cmds.circle(r=0.1,ch=False,n=(prefix+'_cnt'))
    shp=cmds.circle(o=True,r=1,ch=False,d=1,s=4,n=(prefix+'_shp'))
    
    #setup shp
    cmds.move(-1,-1,0,'%s.cv[0]' % shp[0],r=True,os=True)
    cmds.move(-1,-1,0,'%s.cv[4]' % shp[0],r=True,os=True)
    cmds.move(0,-1,0,'%s.cv[1]' % shp[0],r=True,os=True)
    cmds.move(0,0,0,'%s.cv[2]' % shp[0],r=True,os=True)
    cmds.move(-1,0,0,'%s.cv[3]' % shp[0],r=True,os=True)
    
    cmds.parent(shp,grp)
    
    cmds.setAttr('%s.overrideEnabled' % shp[0],1)
    cmds.setAttr('%s.overrideDisplayType' % shp[0],2)
    
    #setup cnt
    cmds.parent(cnt,shp)
    
    cmds.setAttr('%s.overrideEnabled' % cnt[0],1)
    
    cmds.transformLimits(cnt,tx=(-1,0),etx=(1,1))
    cmds.transformLimits(cnt,ty=(-1,0),ety=(1,1))
    
    setupAttrs(prefix,cnt[0])
    
    return grp
    
    cmds.undoInfo(closeChunk=True)