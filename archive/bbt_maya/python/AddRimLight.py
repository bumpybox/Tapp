import maya.cmds as mc

def addRimRamp():

    #get the selection
    currentSelection = mc.ls( selection=True )
    
    #check if there's a texture node (file, ramp, checker etc., etc.)
    if (len(currentSelection) >0) and mc.objExists(currentSelection[0] + ".colorOffset"):
    
        #there is, so create a ramp and sampler info node
        ramp = mc.createNode( "ramp" )
        samplerInfo = mc.shadingNode("samplerInfo", asUtility=True)
        
        #plug them in
        mc.connectAttr( ramp + ".outColor" , currentSelection[0] + ".colorOffset" )
        mc.connectAttr( (samplerInfo + '.facingRatio'), (ramp + '.uCoord') )
        mc.connectAttr( (samplerInfo + '.facingRatio'), (ramp + '.vCoord') )
        
        #set some defaults
        mc.setAttr( ramp + ".colorEntryList[0].color", 1, 0.96, 0, type="double3")
        mc.setAttr( ramp + ".colorEntryList[1].color", 1, 0.22, 0, type="double3")
        mc.setAttr( ramp + ".colorEntryList[2].color", 0, 0, 0, type="double3")
        mc.setAttr( ramp + ".colorEntryList[1].position", 0.1)
        mc.setAttr( ramp + ".colorEntryList[2].position", 0.485)
	
    #there is no texture node, so add a ramp.
    elif (len(currentSelection) >0) and mc.objExists(currentSelection[0] + ".color"):
    
        #get current colour and make new ones based on it
        colour = mc.getAttr(currentSelection[0] + ".color")
        colour2 = [colour[0][0] + ((1-colour[0][0]) * 0.7),colour[0][1] + ((1-colour[0][1]) * 0.6),colour[0][2] + ((1-colour[0][2]) * 0.5)]
        colour3 = [colour2[0] + ((1-colour2[0]) * 0.6),colour2[1] + ((1-colour2[1]) * 0.6),colour2[2] + ((1-colour2[2]) * 0.6)]
        
        #create ramp and sampler info node
        ramp = mc.createNode( "ramp" )
        samplerInfo = mc.shadingNode("samplerInfo", asUtility=True)
        
        #make the connections
        mc.connectAttr( ramp + ".outColor" , currentSelection[0] + ".color" )
        mc.connectAttr( (samplerInfo + '.facingRatio'), (ramp + '.uCoord') )
        mc.connectAttr( (samplerInfo + '.facingRatio'), (ramp + '.vCoord') )
        
        #set ramp colours
        mc.setAttr( ramp + ".colorEntryList[0].color", colour3[0], colour3[1], colour3[2], type="double3")
        mc.setAttr( ramp + ".colorEntryList[1].color", colour2[0], colour2[1], colour2[2], type="double3")
        mc.setAttr( ramp + ".colorEntryList[2].color", colour[0][0], colour[0][1], colour[0][2], type="double3")
        mc.setAttr( ramp + ".colorEntryList[1].position", 0.1)
        mc.setAttr( ramp + ".colorEntryList[2].position", 0.485)
    else:
        mc.warning("Please select a Material or texutre node, i.e. a Vray Mtl, File, Ramp, Checker, Noise etc., node.")
		
        
'''
Usage:
Place the .py file in your scripts folder.
Select a material or a texture node.
In Mel: 
python "import AddRimLight"; python "AddRimLight.addRimRamp()";
In Python: 
import AddRimLight
AddRimLight.addRimRamp()
'''