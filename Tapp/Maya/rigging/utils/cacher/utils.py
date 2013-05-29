import os
import xml.etree.ElementTree as xml

import maya.cmds as cmds

from bbt_maya.brt import utils

def getSkinData():
    ''' Returns meta data,tranform and shapes nodes as dict relating to the skin node '''
    
    skinData=[]
    for node in cmds.ls(type='network'):
        
        meta=utils.meta()
        
        data=meta.getData(node)
        
        if data['type']=='skin':
            
            info={}
            
            transformNode=cmds.listConnections('%s.message' % node,type='transform')[0]
            shapeNode=cmds.listRelatives(transformNode,s=True)[-1]
            
            info['meta']=node
            info['transform']=transformNode
            info['shape']=shapeNode
            info['component']=data['component']
            
            skinData.append(info)
    
    return skinData

def exportCache():
    ''' Export a cache file for all tagged skin nodes in scene '''
    
    # creating folder for cache files
    projectDir=cmds.workspace(listWorkspaces=True)[-1]
    dataDir=projectDir+'/data'
    
    if os.path.exists(dataDir)!=True:
        os.makedirs(dataDir)
    
    # getting skin data
    skinData=getSkinData()
    skinNodes=[]
    for node in skinData:
        skinNodes.append(node['shape'])
    
    # exporting cache
    fName=cmds.file(q=True,sceneName=True,shortName=True).split('.')[0]
    
    sFrame=cmds.playbackOptions(animationStartTime=True,q=True)
    eFrame=cmds.playbackOptions(animationEndTime=True,q=True)
    
    cmds.cacheFile(fileName=fName,pts=skinNodes,dir=dataDir,singleCache=True,staticCache=True,
                   worldSpace=True,startTime=sFrame,endTime=eFrame,format='OneFile')
    
    # modifying xml cache file, adding meta data
    xmlFile=dataDir+'/'+fName+'.xml'
    
    tree = xml.parse(xmlFile)
    root = tree.getroot()
    channels=root.find('Channels')
    
    for channel in channels:
        for node in skinData:
            if channel.get('ChannelName')==node['shape']:
                channel.set('component',node['component'])
    
    tree.write(xmlFile)

def importCache(xmlFile):
    
    pass