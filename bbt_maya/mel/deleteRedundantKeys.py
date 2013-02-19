# script created by pymel.tools.mel2py from mel file:
# C:\Users\render\Documents\GitHub\Tapp\bbt_maya\mel\deleteRedundantKeys.mel

from pymel.all import *
#////////////////////////////////
#
# Maya script file
#
#////////////////////////////////
#
# Author : LluLlobera
#	    (lluisllobera@gmail.com)
#
# Creation date : 23/III/2006
#          v1.1 : 24/III/2006
#          v1.2 : 18/X/2006
#
# Main procedure : type "llDeleteRedundantKeys" in the Command Line or Script Editor
#
#////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////
#
#
#   DESCRIPTION
#
# This script will delete the "redundant" keys in the curves seen in the Graph Editor, or else
# in the whole scene if no curves are seen in the Graph Editor.
#
# "Redundant" keys are those which are not useful for the changes in the animation - i.e.
# consecutive flat keys with the same value, stepped keys, and so on.
#
# Thanks to my mentor Victor Navone for the idea .. another lifesaver !
#
#
#   VERSION HISTORY
#
# UPDATE 1.1 : added new case for redundant-ness. If the angle of the tangents of three
# consecutive keys that are not stepped is the same (within a tolerance limit of 0.0001), 
# the middle key is considered redundant and deleted
#
# UPDATE 1.2 : if any keyframes are selected in the Graph Editor, now the script will 
# clean only those. Otherwise, it will clean the visible curves in the GE, or the whole 
# scene's curves if none are visible in the GE. Also, upon deleting redundant keys, 
# now the script's output message reflects the exact number of curves that were actually
# cleaned, instead of the total sum of curves it iterated through.
# 
#
#		Enjoy!!
#
#
#//////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////
#  llDRKNameIsChannel          //
#////////////////////////////////
# 
# Returns 0 if the input name is an object,
# or 1 if it is an attribute.
#
#
# <-- llDRKFilterChannels
#
#////////////////////////////////
def llDRKNameIsChannel(NAME):
	RETURN=0
	SUBSTRING=''
	for I in range(1,(len(NAME) - 1)+1):
		SUBSTRING=str(mel.eval("substring " + NAME + " " + str(I) + " " + str(I)))
		if SUBSTRING == ".":
			RETURN=1
			
		
	
	# for
	return RETURN
	


# global proc int llDRKNameIsChannel
#////////////////////////////////
#  llDRKFilterChannels         //
#////////////////////////////////
# 
# Goes through the names input by $CHANNELS and checks if they are channels or objects.
# If they are objects, their keyable attributes are added to $CHANNELS, and the object's
# name itself is blanked out with an empty string ("") from the list.
# 
#
# <-- llDeleteRedundantKeys
# --> llDRKNameIsChannel
#
#////////////////////////////////
def llDRKFilterChannels(CHANNELS):
	SIZE=len(CHANNELS)
	if SIZE>0:
		for I in range(0,SIZE - 1+1):
			if not llDRKNameIsChannel(CHANNELS[I]):
				ATTS=listAttr(k=CHANNELS[I])
				for ATT in ATTS:
					CURVENAME=mel.eval("listConnections -type animCurve " + CHANNELS[I] + "." + str(ATT))
					if len(CURVENAME)>0:
						CHANNELS[(len(CHANNELS))]=CHANNELS[I] + "." + str(ATT)
						
					
				
				# for ($ATT in $ATTS)
				CHANNELS[I]=""
				
			
			# if
			
		
		# for
		
	
	# if ($SIZE > 0)
	return CHANNELS
	


# global proc llDRKFilterChannels
#////////////////////////////////
#  llDRKCleanChannel           //
#////////////////////////////////
# 
# Gets all the useful data from the specified channel,
# then loops through all its keys getting rid of the redundant ones.
# 
#
# <-- llDeleteRedundantKeys
#
#////////////////////////////////
def llDRKCleanChannel(CHANNEL):
	COUNT=0
	# initialize counter
	# get selected keys from specified channel
	MIN=0
	SELECTED=keyframe(CHANNEL,
		q=1,iv=1,sl=1)
	if len(SELECTED) == 0:
		MIN=1
		SELECTED=keyframe(CHANNEL,
			q=1,iv=1)
		
	
	# get necessary data from animation curve
	VALUE=keyframe(CHANNEL,
		q=1,vc=1)
	TIME=keyframe(CHANNEL,
		q=1,tc=1)
	INTYPE=keyTangent(CHANNEL,
		q=1,itt=1)
	OUTTYPE=keyTangent(CHANNEL,
		q=1,ott=1)
	INANGLE=keyTangent(CHANNEL,
		q=1,ia=1)
	OUTANGLE=keyTangent(CHANNEL,
		q=1,oa=1)
	INWEIGHT=keyTangent(CHANNEL,
		q=1,iw=1)
	OUTWEIGHT=keyTangent(CHANNEL,
		q=1,ow=1)
	INX=keyTangent(CHANNEL,
		q=1,ix=1)
	INY=keyTangent(CHANNEL,
		q=1,iy=1)
	OUTX=keyTangent(CHANNEL,
		q=1,ox=1)
	OUTY=keyTangent(CHANNEL,
		q=1,oy=1)
	# change linear tolerance of Maya to get less decimals in the angle output
	# (tolerance get restored in the end of the proc)
	TOLERANCE=float(tolerance(q=1,l=1))
	NEWTOLERANCE=0.0001
	tolerance(l=NEWTOLERANCE)
	# initialize $PURGE variable
	PURGE=float(0)
	# proceed only if there's more than one key
	if len(VALUE)>1:
		if MIN == 0:
			if SELECTED[0] == 0:
				LASTVALUE=VALUE[(SELECTED[0])]
				
			
			else:
				LASTVALUE=VALUE[(SELECTED[0]) - 1]
				
			
		
		else:
			LASTVALUE=0
			
		for J in range(MIN,(len(SELECTED) - 1)+1):
			I=SELECTED[J]
			if I != 0:
				PURGE=float(0)
				if VALUE[I] == LASTVALUE:
					if (OUTY[I - 1] == 0) and (INY[I] == 0) and (OUTY[I] == 0) and (INY[I + 1] == 0) and (VALUE[I + 1] == VALUE[I]):
						PURGE=float(1)
						# case 1 : tangents are flattened
						# previous out is 0
						# current in-out is 0
						# next in is 0
						# next value is the same
						
					
					# case 2 : stepped tangents
					elif (OUTTYPE[I - 1] == "step") and (OUTTYPE[I] == "step") and (OUTTYPE[I + 1] != "spline"):
						PURGE=float(2)
						# previous out is step
						# current out is step
						# next out is not spline
						
					
				
				# if
				# case 3 : same angle
				elif (OUTTYPE[I - 1] != "step") and (mel.equivalent(OUTANGLE[I - 1], INANGLE[I])) and (OUTANGLE[I - 1] != 0) and (OUTTYPE[I] != "step") and (mel.equivalent(INANGLE[I], OUTANGLE[I])) and (mel.equivalent(OUTANGLE[I], INANGLE[I + 1])):
					PURGE=float(3)
					# previous out is not step
					# previous out is same as current in
					# previous out is not 0
					# current out is not step
					# current in is same as current out
					# current out is same as next in
					
				
				else:
					LASTVALUE=VALUE[I]
					
				if PURGE != 0:
					cutKey(CHANNEL,
						t=TIME[I])
					# delete key
					# copy values from previous key
					VALUE[I]=VALUE[I - 1]
					TIME[I]=TIME[I - 1]
					INTYPE[I]=INTYPE[I - 1]
					OUTTYPE[I]=OUTTYPE[I - 1]
					INANGLE[I]=INANGLE[I - 1]
					INANGLE[I]=OUTANGLE[I - 1]
					INWEIGHT[I]=INWEIGHT[I - 1]
					OUTWEIGHT[I]=OUTWEIGHT[I - 1]
					INX[I]=INX[I - 1]
					INY[I]=INY[I - 1]
					OUTX[I]=OUTX[I - 1]
					OUTY[I]=OUTY[I - 1]
					# increase counter
					COUNT=COUNT + 1
					
				
				# if ($PURGE != 0)
				
			
			# if ($I != 0)
			
		
		# for
		
	
	# if
	# restore tolerance
	tolerance(l=TOLERANCE)
	# return number of redundant keys found
	return COUNT
	


# global proc int llDRKCleanChannel
#////////////////////////////////
#  llDeleteRedundantKeys       //
#////////////////////////////////
# 
# MAIN PROC
# 
# Calls on the proc to clean individual channels.
# If no curves are visible in the Graph Editor, 
# a confirm dialog will pop up asking the user 
# if they want to run the script on all 
# the animation curves in the scene.
# 
#
# --> llDRKCleanChannel
# --> llDRKFilterChannels
#
#////////////////////////////////
def llDeleteRedundantKeys():
	CHANNELS_SELECTED=1
	CHANNELS=keyframe(q=1,sl=1,n=1)
	if len(CHANNELS) == 0:
		CHANNELS=selectionConnection('graphEditor1FromOutliner',q=1,obj=1)
		CHANNELS_SELECTED=0
		
	
	# if (`size $CHANNELS` == 0)
	COUNT=0
	CURVES=0
	ADD=0
	if len(CHANNELS)>0:
		if not CHANNELS_SELECTED:
			CHANNELS=llDRKFilterChannels(CHANNELS)
			
		for CHANNEL in CHANNELS:
			if CHANNEL != "":
				ADD=0
				ADD+=int(mel.eval("llDRKCleanChannel \"" + str(CHANNEL) + "\""))
				COUNT+=ADD
				if ADD>0:
					CURVES+=1
					
				
			
		
		# if
		
	
	# if (`size $CHANNELS` > 0)
	else:
		ANSWER=str(confirmDialog(title="Delete All Redundant Keys",
			cancelButton="Cancel",defaultButton="Yes",button=["Yes", "No"],
			message="Delete redundant keys for all the animation curves in the scene ?",
			dismissString="Cancel"))
		if ANSWER == "Yes":
			CHANNELS=ls(type='animCurve')
			if len(CHANNELS)>0:
				for CHANNEL in CHANNELS:
					if not referenceQuery(isNodeReferenced=CHANNEL):
						ADD=0
						ADD+=int(mel.eval("llDRKCleanChannel \"" + str(CHANNEL) + "\""))
						COUNT+=ADD
						if ADD>0:
							CURVES+=1
							
						
					
				
			
			# if
			
		
		# if
		else:
			COUNT=-1
			
		
	
	# else
	# output counting result
	if COUNT>0:
		print "// Result : cleaned " + str(COUNT) + " redundant keys in " + str(CURVES) + " animation curves //\n"
		
	
	elif COUNT == 0:
		print "// Result : no redundant keys found //\n"
		
	


# global proc llDeleteRedundantKeys
#//////////////////////////////////////////////////////////////////////////////////////////////////
#
# EoS llDeleteRedundantKeys
#
#//////////////////////////////////////////////////////////////////////////////////////////////////
