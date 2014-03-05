################################################################
# 
# Ken Perlin's page: http://mrl.nyu.edu/~perlin/noise/
# Perlin script setup by Paulalso
# Updated by Ian Waters: http://ianwaters.posterous.com/
#
#---------------------------------------------------------------
# Usage: Run the following example setup script
# import maya.cmds
# maya.cmds.loadPlugin("basicPerlinDeformer.py")
# maya.cmds.polySphere( r=5.0, sx=20, sy=20, ax=[0,1,0] )
# maya.cmds.deformer( type='basicPerlinDeformer' )
#################################################################

# import the maya and python modules we will derive from
import math, sys, random
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx

# our plugin's name
kPluginNodeTypeName = "basicPerlinDeformer"

# our plugin's unique Id number in hex form
noiseDeformId = OpenMaya.MTypeId( 0x00372 )

# Ken's permutation array composed of 512 elements = 2 sets of (0,255)
p = [151,160,137, 91, 90, 15,131, 13,201, 95, 96, 53,194,233,  7,225,
	 140, 36,103, 30, 69,142,  8, 99, 37,240, 21, 10, 23,190,  6,148,
	 247,120,234, 75,  0, 26,197, 62, 94,252,219,203,117, 35, 11, 32,
	  57,177, 33, 88,237,149, 56, 87,174, 20,125,136,171,168, 68,175,
	  74,165, 71,134,139, 48, 27,166, 77,146,158,231, 83,111,229,122,
	  60,211,133,230,220,105, 92, 41, 55, 46,245, 40,244,102,143, 54,
	  65, 25, 63,161,  1,216, 80, 73,209, 76,132,187,208, 89, 18,169,
	 200,196,135,130,116,188,159, 86,164,100,109,198,173,186,  3, 64,
	  52,217,226,250,124,123,  5,202, 38,147,118,126,255, 82, 85,212,
	 207,206, 59,227, 47, 16, 58, 17,182,189, 28, 42,223,183,170,213,
	 119,248,152,  2, 44,154,163, 70,221,153,101,155,167, 43,172,  9,
	 129, 22, 39,253, 19, 98,108,110, 79,113,224,232,178,185,112,104,
	 218,246, 97,228,251, 34,242,193,238,210,144, 12,191,179,162,241,
	  81, 51,145,235,249, 14,239,107, 49,192,214, 31,181,199,106,157,
	 184, 84,204,176,115,121, 50, 45,127,  4,150,254,138,236,205, 93,
	 222,114, 67, 29, 24, 72,243,141,128,195, 78, 66,215, 61,156,180,
	 151,160,137, 91, 90, 15,131, 13,201, 95, 96, 53,194,233,  7,225,
	 140, 36,103, 30, 69,142,  8, 99, 37,240, 21, 10, 23,190,  6,148,
	 247,120,234, 75,  0, 26,197, 62, 94,252,219,203,117, 35, 11, 32,
	  57,177, 33, 88,237,149, 56, 87,174, 20,125,136,171,168, 68,175,
	  74,165, 71,134,139, 48, 27,166, 77,146,158,231, 83,111,229,122,
	  60,211,133,230,220,105, 92, 41, 55, 46,245, 40,244,102,143, 54,
	  65, 25, 63,161,  1,216, 80, 73,209, 76,132,187,208, 89, 18,169,
	 200,196,135,130,116,188,159, 86,164,100,109,198,173,186,  3, 64,
	  52,217,226,250,124,123,  5,202, 38,147,118,126,255, 82, 85,212,
	 207,206, 59,227, 47, 16, 58, 17,182,189, 28, 42,223,183,170,213,
	 119,248,152,  2, 44,154,163, 70,221,153,101,155,167, 43,172,  9,
	 129, 22, 39,253, 19, 98,108,110, 79,113,224,232,178,185,112,104,
	 218,246, 97,228,251, 34,242,193,238,210,144, 12,191,179,162,241,
	  81, 51,145,235,249, 14,239,107, 49,192,214, 31,181,199,106,157,
	 184, 84,204,176,115,121, 50, 45,127,  4,150,254,138,236,205, 93,
	 222,114, 67, 29, 24, 72,243,141,128,195, 78, 66,215, 61,156,180]

# Ken's Utility functions for noise
# linear interpolation
def lerp(parameter=0.5,value1=0.0,value2=1.0):
	return value1 + parameter * (value2 - value1)

# Ken's new spline interpolation
def fade(parameter=1.0):
	return parameter*parameter*parameter*(parameter*(parameter*6.0 - 15.0) + 10.0)

# Ken's new function to return gradient values
# based on bit operations on hashId
def grad(hashId=255,x=1.0,y=1.0,z=1.0):
	h = hashId & 15
	if (h < 8):
		u = x
	else:
		u = y
		
	if (h < 4):
		v = y
	elif (h==12 or h==14):
		v = x
	else:
		v = z
	if ((h&1)!=0):
		u = -u
	if ((h&2)!=0):
		v = -v
	return u + v

# Ken's improved gradient noise function
def improvedGradNoise(vx=1.0,vy=1.0,vz=1.0):
	# get integer lattice values for sample point position
	X = int(math.floor(vx)) & 255
	Y = int(math.floor(vy)) & 255
	Z = int(math.floor(vz)) & 255
	# fractional part of point position
	vx -= math.floor(vx)
	vy -= math.floor(vy)
	vz -= math.floor(vz)
	# interpolate fractional part of point position
	u = fade(vx)
	v = fade(vy)
	w = fade(vz)
	# new hash integer lattice cell coords onto perm array
	A = p[X]+Y
	B = p[X+1]+Y
	AA = p[A]+Z
	BA = p[B]+Z
	AB = p[A+1]+Z
	BB = p[B+1]+Z
	# new hash onto gradients
	gradAA  = grad(p[AA],   vx,     vy,     vz  )
	gradBA  = grad(p[BA],   vx-1.0, vy,     vz  )
	gradAB  = grad(p[AB],   vx,     vy-1.0, vz  )
	gradBB  = grad(p[BB],   vx-1.0, vy-1.0, vz  )
	gradAA1 = grad(p[AA+1], vx,     vy,     vz-1.0)
	gradBA1 = grad(p[BA+1], vx-1.0, vy,     vz-1.0)
	gradAB1 = grad(p[AB+1], vx,     vy-1.0, vz-1.0)
	gradBB1 = grad(p[BB+1], vx-1.0, vy-1.0, vz-1.0)
	# trilinear intropolation of resulting gradients to sample point position
	result = lerp(w, lerp(v, lerp(u, gradAA, gradBA), lerp(u, gradAB, gradBB)), lerp(v, lerp(u, gradAA1, gradBA1), lerp(u, gradAB1, gradBB1)))
	return result

# Node definition
class basicPerlinDeformer(OpenMayaMPx.MPxDeformerNode):
	
	# class variables
	freq = OpenMaya.MObject()
	multiplierX = OpenMaya.MObject()
	multiplierY = OpenMaya.MObject()
	multiplierZ = OpenMaya.MObject()
	aPlaceMat = OpenMaya.MObject()
	time = OpenMaya.MObject()
	
	# node constructor
	def __init__(self):
		OpenMayaMPx.MPxDeformerNode.__init__(self)
		
	# deform method must be specificed by you
	def deform(self,dataBlock,geomIter,matrix,multiIndex):
		# get the frequency and amplitudes from the datablock
		freqValue = dataBlock.inputValue( self.freq ).asDouble()
				
		multXValue = dataBlock.inputValue( self.multiplierX ).asDouble()
				
		multYValue = dataBlock.inputValue( self.multiplierY ).asDouble()
				
		multZValue = dataBlock.inputValue( self.multiplierZ ).asDouble()
				
		# get the seed and octaves from the datablock
		octaves	= dataBlock.inputValue(self.octaves).asInt()
		seed 	= dataBlock.inputValue(self.seed).asLong()
		
		# get matrix
		matrixHandle = dataBlock.inputValue( self.aPlaceMat )
		mat = matrixHandle.asMatrix()
		matInv = mat.inverse()
		
		# get the built-in deformer envelope
		envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
		envelopeHandle = dataBlock.inputValue( envelope )
		envelopeValue = envelopeHandle.asFloat()
		
		# iterate over the object's points
		freqValue *= 0.05#a simple scale factor to give better control over the freq range.
		
		#get all the points on the object
		allPoints = OpenMaya.MPointArray()
		while geomIter.isDone() == False:
			point = geomIter.position()
			
			# transform the point position, doesn't really matter here, but it's best pratice
			point *= matInv
			
			#get the slider values
			aplitudeX = multXValue
			aplitudeY = multYValue
			aplitudeZ = multZValue
			freqX = freqValue
			freqY = freqValue
			freqZ = freqValue
			
			#reset the noise variables
			noiseX = 0	
			noiseY = 0
			noiseZ = 0
			
			# get weight value for the point
			weights = self.weightValue(dataBlock, multiIndex, geomIter.index())
			
			# make the noise, repeat for as many octaves as we have, doubling the frequency and halving the amplitude each time.
			for _ in range(octaves):
				noiseX += improvedGradNoise( point.x*freqX+seed, point.y*freqX+seed, point.z*freqX+seed ) * weights * envelopeValue * aplitudeX
				noiseY += improvedGradNoise( point.x*freqY+250+seed, point.y*freqY+500+seed, point.z*freqY+500+seed ) * weights * envelopeValue * aplitudeY
				noiseZ += improvedGradNoise( point.x*freqZ+500+seed, point.y*freqZ+250+seed, point.z*freqZ+250+seed ) * weights * envelopeValue * aplitudeZ
				freqX *=2
				freqY *=2
				freqZ *=2
				aplitudeX /= 2
				aplitudeY /= 2
				aplitudeZ /= 2
				
			# add the noise to the point position					
			point.x += noiseX
			point.y += noiseY
			point.z += noiseZ
			# transform back to world space
			point *= mat
			# store the new position ready to set it later (line 216)
			allPoints.append(point)
			geomIter.next()	
			
		#set all the new point positions at once rather then one at a time (it's much faster).	
		geomIter.setAllPositions(allPoints)		
		
	# these are methods you have to provide for connecting your deformer to a control object		
	def accessoryAttribute( self ):
		thisNode = self.thisMObject()
		fnThisNode = OpenMaya.MFnDependencyNode(thisNode)
		thisNodeMat = fnThisNode.attribute( "placementMatrix" )
		return thisNodeMat
		
	# these are methods you have to provide for connecting your deformer to a control object
	# since this is a 3d noise I am using the 3d texture doo-hickey-thing-a-ma-bob
	# we simply connect the matrix attributes so it will control our noise placement in 3d space.
	def accessoryNodeSetup( self, cmd ):
		loc = OpenMaya.MObject()
		try:
			objLoc = cmd.createNode( "place3dTexture",loc )
			fnLoc = OpenMaya.MFnDependencyNode( objLoc )
			attrMat = fnLoc.attribute( "matrix" )
			thisNode = self.thisMObject()
			fnThisNode = OpenMaya.MFnDependencyNode(thisNode)
			thisNodeMat = fnThisNode.attribute( "placementMatrix" )
			cmd.connect( objLoc, attrMat, thisNode, thisNodeMat )
			cmd.renameNode( objLoc, 'place3dNoise#' )
		except:
			sys.stderr.write( "Failed to create locator and connections for %s node\n", kPluginNodeTypeName )

# node creator
def nodeCreator():
	return OpenMayaMPx.asMPxPtr( basicPerlinDeformer() )

# node initializer
def nodeInitializer():
	# Create Attributes
	# frequency or texture scale factor
	nAttr = OpenMaya.MFnNumericAttribute()
	basicPerlinDeformer.freq = nAttr.create( "frequency", "fq", OpenMaya.MFnNumericData.kDouble, 20.0 )
	nAttr.setMin(0.0)
	nAttr.setSoftMax(100.0)
	nAttr.setKeyable(True)
	nAttr.setStorable(True)
	
	# amplitude multiplier's for each axis.
	nAttr = OpenMaya.MFnNumericAttribute()
	basicPerlinDeformer.multiplierX = nAttr.create( "amplitudeX", "aX", OpenMaya.MFnNumericData.kDouble, 0.5 )
	nAttr.setSoftMin(-10.0)
	nAttr.setSoftMax(10.0)
	nAttr.setKeyable(True)
	nAttr.setStorable(True)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	basicPerlinDeformer.multiplierY = nAttr.create( "amplitudeY", "aY", OpenMaya.MFnNumericData.kDouble, 0.5 )
	nAttr.setSoftMin(-10.0)
	nAttr.setSoftMax(10.0)
	nAttr.setKeyable(True)
	nAttr.setStorable(True)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	basicPerlinDeformer.multiplierZ = nAttr.create( "amplitudeZ", "aZ", OpenMaya.MFnNumericData.kDouble, 0.5 )
	nAttr.setSoftMin(-10.0)
	nAttr.setSoftMax(10.0)
	nAttr.setKeyable(True)
	nAttr.setStorable(True)
	
	# random seed and octaves.
	nAttr = OpenMaya.MFnNumericAttribute()
	basicPerlinDeformer.seed = nAttr.create( "randomSeed", "seed", OpenMaya.MFnNumericData.kInt, 0 )
	nAttr.setStorable(True)
	nAttr.setKeyable(True)
	nAttr.setMin(0)
	nAttr.setSoftMin(0.0)
	nAttr.setSoftMax(100.0)
	nAttr.setStorable(True)
	
	nAttr = OpenMaya.MFnNumericAttribute()
	basicPerlinDeformer.octaves = nAttr.create( "octaves", "oct", OpenMaya.MFnNumericData.kInt, 2 )
	nAttr.setStorable(True)
	nAttr.setKeyable(True)
	nAttr.setMin(1)
	nAttr.setSoftMin(1.0)
	nAttr.setSoftMax(10.0)
	nAttr.setStorable(True)
	
	mAttr = OpenMaya.MFnMatrixAttribute()
	basicPerlinDeformer.aPlaceMat = mAttr.create("placementMatrix", "pm")
	mAttr.setHidden(True)

	
	# add attributes to node and set attribute dependencies
	try:
		basicPerlinDeformer.addAttribute( basicPerlinDeformer.freq )
		basicPerlinDeformer.addAttribute( basicPerlinDeformer.seed )
		basicPerlinDeformer.addAttribute( basicPerlinDeformer.multiplierX )
		basicPerlinDeformer.addAttribute( basicPerlinDeformer.multiplierY )
		basicPerlinDeformer.addAttribute( basicPerlinDeformer.multiplierZ )
		basicPerlinDeformer.addAttribute( basicPerlinDeformer.octaves )
		basicPerlinDeformer.addAttribute( basicPerlinDeformer.aPlaceMat )
		
		#tell the node to recalculate when the attribute values are changed.
		outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
		basicPerlinDeformer.attributeAffects( basicPerlinDeformer.freq, outputGeom )
		basicPerlinDeformer.attributeAffects( basicPerlinDeformer.multiplierX, outputGeom )
		basicPerlinDeformer.attributeAffects( basicPerlinDeformer.multiplierY, outputGeom )
		basicPerlinDeformer.attributeAffects( basicPerlinDeformer.multiplierZ, outputGeom )
		basicPerlinDeformer.attributeAffects( basicPerlinDeformer.octaves, outputGeom )
		basicPerlinDeformer.attributeAffects( basicPerlinDeformer.seed, outputGeom )
		basicPerlinDeformer.attributeAffects( basicPerlinDeformer.aPlaceMat, outputGeom )
	except:
		sys.stderr.write( "Failed to create attributes of %s node\n", kPluginNodeTypeName )
	
	#make the point weights available for painting via Modify > Paint Attributes Tool
	OpenMaya.MGlobal.executeCommand( "makePaintable -attrType multiFloat -sm deformer basicPerlinDeformer weights;" );
	
# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerNode( kPluginNodeTypeName, noiseDeformId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode )
	except:
		sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )

# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode( noiseDeformId )
	except:
		sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )
