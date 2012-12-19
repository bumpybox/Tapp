import os
import xml.etree.ElementTree as xml

import maya.cmds as cmds

from bbt_maya import generic

class cache():

    def alembicExport(self,startFrame,endFrame,fileName,fileDir,nodes):
        ''' Exports alembic file with meta data file (*.abcMeta) '''
        
        # defining variables
        meta=generic.Meta()
        nodesString=''
        root=xml.Element('root')
        
        # node loop
        for node in nodes:
            nodesString+='-root '+node+' '
            
            data=meta.getData(node)
            
            # xml build
            node=xml.Element('node')
            root.append(node)
            
            for d in data:
                
                if data[d]==None:
                    node.attrib[d]='None'
                else:
                    node.attrib[d]=data[d]
        
        # export alembic file
        filePath=fileDir+'/'+fileName+'.abc'
        cmds.AbcExport(j='-frameRange %s %s -worldSpace %s-file %s' % (startFrame,endFrame,nodesString,filePath))
        
        #export meta data file
        filePath=fileDir+'/'+fileName+'.abcMeta'
        file=open(filePath,'w')
        
        xml.ElementTree(root).write(file)
        
        file.close()

sFrame=1
eFrame=100
fileName='temp'
fileDir='C:/Users/Toke/Desktop'
nodes=['goldFish_face:l_eyeball_geo','goldfish_geo:body']

c=cache()
c.alembicExport(sFrame, eFrame, fileName, fileDir, nodes)