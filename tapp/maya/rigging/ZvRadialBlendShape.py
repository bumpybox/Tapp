"""ZV Radial Blend Shape

Copyright (C) 2010 Paolo Dominici

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Usage:
import zvRadialBlendShape
zvRadialBlendShape.zvRadialBlendShape()
"""

__product__ = 'ZV Radial Blend Shape'
__copyright__ = 'Copyright (c) 2010 Paolo Dominici'
__author__ = 'Paolo Dominici (paolodominici@gmail.com)'
__version__ = '3.0.0'
__date__ = '2014/05/04'


import sys, webbrowser
from maya import cmds

# change the following suffixes as you like
_rbsNodeName = 'radialBlendShape'
_eyelidLocSfx = '_lid_loc'
_eyeLocSfx = '_eye_loc'
_eyeParentLocSfx = '_eyeRest_loc'
_headGrpSfx = '_parentToHead_grp'
_eyelidGrpName = '_lid_grp'
_locGrpName = '%s_grp' % _rbsNodeName

_controls = {}
_labelList = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_orderedLabelList = 'LRABCDEFGHIJKMNOPQSTUVWXYZ'

_autoMembTolerance = 0.0001

# the following names match the attribute names from the deformer node, do not touch!
_attrs = ['blend', 'twist', 'follow', 'followMaxAngle', 'followOpen', 'followClose', 'maxDisplacement']
_blinkAttrs = ['blink', 'blinkBias']
_bulgeAttrs = ['bulgeDisplacement', 'bulgeRadius']
_offsetAttrs = ['offsetIn', 'offsetMid', 'offsetOut']
_offsetInfluenceAttrs = ['offsetInfluenceAngle']
_targetAttrs = ['inputMesh', 'inputOppositeMesh', 'inputMatrix', 'eyeMatrix', 'eyeParentMatrix', 'targetWeights']
_computeDispAttr = 'computeDisplacements'
_defAttrValues = [0.0, 0.0, 1.0, 40.0, 0.2, 0.2, -1.0]
_defBulgeValues = [0.5, 30.0]
_defOffsetInfluenceValues = [120.0]
_wAttr = _targetAttrs[-1]

def cb(func, *args):
	return '%s.%s(%s)' % (func.__module__, func.__name__, ', '.join([repr(s) for s in args]))

def _getMembershipSet(rbsNode):
	return cmds.listConnections('%s.message' % rbsNode, type='objectSet', s=False)[0]

def _parent(obj, parent):
	objParentList = cmds.listRelatives(obj, p=True, pa=True)
	if objParentList and objParentList[0] == parent:
		return obj
	
	return cmds.parent(obj, parent, r=True)[0]

def _setAlias(attr, alias):
	if cmds.aliasAttr(attr, q=True) != alias:
		cmds.aliasAttr(alias, attr)

def _getEyeIdxList(rbsNode):
	return _getAttrIdxList(rbsNode, 'it')

def _getAttrIdxList(rbsNode, attrName):
	return cmds.getAttr('%s.%s' % (rbsNode, attrName), mi=True) or []

def _getEyeIdxPrfxList(rbsNode):
	"""Returns the eye prefixes (like (0, 'L') or (2, 'R'))."""
	
	miList = _getEyeIdxList(rbsNode)
	nameList = [(idx, _getTargetNameFromIdx(rbsNode, idx)) for idx in miList]
	result = []
	for idx, name in nameList:
		if name:
			elem = (idx - (idx%2), name[0])
			if not elem in result:
				result.append(elem)
			
	return result

def _getTargetNameFromIdx(rbsNode, idx):
	"""Returns the input target name from the given index."""
	return cmds.aliasAttr('%s.it[%d]' % (rbsNode, idx), q=True) or None

def _getSelectedShape(shapeType=None):
	if shapeType:
		sel = cmds.ls(sl=True, typ=shapeType) or cmds.listRelatives(s=True, ni=True, pa=True, typ=shapeType)
	else:
		sel = cmds.ls(sl=True, shapes=True) or cmds.listRelatives(s=True, ni=True, pa=True)
	
	return sel and cmds.listRelatives(sel[0], p=True, pa=True)[0] or None

def _getRbs(geo):
	"""Get rbs from history."""
	
	rbsNodeList = [s for s in cmds.listHistory(geo, pdo=True, il=2) or [] if cmds.nodeType(s) == _rbsNodeName]
	return rbsNodeList and rbsNodeList[0] or None

def _getGeoFromUI():
	return cmds.text(_controls['geo'], q=True, l=True) or None

def _addEyeDialog(rbsNode):
	form = cmds.setParent(q=True)
	
	# used prefixes
	idxPrfxList = _getEyeIdxPrfxList(rbsNode)
	prfxList = [s[1] for s in idxPrfxList]
	
	# available prefixes
	availList = [s for s in _labelList if not s in prfxList]
	
	# preferred prefix
	selPrfx = None
	for prfx in _orderedLabelList:
		if prfx in availList:
			selPrfx = prfx
			break
	
	
	menu = cmds.optionMenu(label='Please choose a name.\nUsually "L" or "R"   ')
	for l in availList:
		cmds.menuItem(label=l)
	if selPrfx:
		cmds.optionMenu(menu, e=True, v=selPrfx)
	
	sep = cmds.separator(style='none')
	b = cmds.button(l='OK', c=lambda *x: cmds.layoutDialog(dismiss=cmds.optionMenu(menu, q=True, v=True)))
	cmds.formLayout(form, e=True, attachForm=[(menu, 'top', 10), (menu, 'left', 10), (menu, 'right', 2), (b, 'bottom', 2), (b, 'left', 2), (b, 'right', 2)], attachControl=[(sep, 'top', 4, menu), (sep, 'bottom', 4, b)])
	
def _mirrorWeightsDialog(rbsNode, destPrfx):
	"""Mirror bulge weights dialog box."""

	form = cmds.setParent(q=True)

	# used prefixes
	idxPrfxList = _getEyeIdxPrfxList(rbsNode)
	prfxList = [s[1] for s in idxPrfxList if s[1] != destPrfx]

	menu = cmds.optionMenu(label='Mirror bulge weights from\n(the current weights will be destroyed):')
	for l in prfxList:
		cmds.menuItem(label=l)

	cmds.optionMenu(menu, e=True, sl=1)

	sep = cmds.separator(style='none')
	b = cmds.button(l='OK', c=lambda *x: cmds.layoutDialog(dismiss=cmds.optionMenu(menu, q=True, v=True)))
	cmds.formLayout(form, e=True, attachForm=[(menu, 'top', 10), (menu, 'left', 10), (menu, 'right', 2), (b, 'bottom', 2), (b, 'left', 2), (b, 'right', 2)], attachControl=[(sep, 'top', 4, menu), (sep, 'bottom', 4, b)])

def _disconnectAndRemoveAttr(attr, remove=False):
	"""Disconnects inputs and outputs from the given attribute."""
	
	sel = cmds.ls(sl=True)
	cmds.select(cl=True)
	
	# unlock if needed
	cmds.setAttr(attr, l=False)
	
	# if any connection, disconnect
	srcAttrs = cmds.listConnections(attr, d=False, p=True) or []
	destAttrs = cmds.listConnections(attr, s=False, p=True) or []
	for srcAttr in srcAttrs:
		cmds.disconnectAttr(srcAttr, attr)
	
	for destAttr in destAttrs:
		cmds.disconnectAttr(attr, destAttr)
	
	# remove element
	if remove:
		cmds.removeMultiInstance(attr)
		
		# remove alias
		if cmds.aliasAttr(attr, q=True):
			cmds.aliasAttr(attr, rm=True)
	
	cmds.select(sel or None)

def _setAttrAliases(rbsNode, idx):
	"""Sets aliases for blend, twist, etc... and remove unused attributes."""
	
	targetName = _getTargetNameFromIdx(rbsNode, idx)
	if not targetName:
		return
	
	# set upper and lower attr names
	for attrName in _attrs + _offsetAttrs:
		if not idx in _getAttrIdxList(rbsNode, attrName):
			continue
		
		attr = '%s.%s[%d]' % (rbsNode, attrName, idx)
		name = '%s_%s' % (targetName, attrName)
		_setAlias(attr, name)
	
	# set common attr names, up only
	for attrName in _bulgeAttrs + _blinkAttrs:
		if not idx in _getAttrIdxList(rbsNode, attrName):
			continue
		
		attr = '%s.%s[%d]' % (rbsNode, attrName, idx)
		name = '%s_%s' % (targetName[0], attrName)
		_setAlias(attr, name)

	# set the up only attributes which are set even if the idx is lower
	for attrName in _offsetInfluenceAttrs:
		upIdx = idx + 1 - idx%2
		if not upIdx in _getAttrIdxList(rbsNode, attrName):
			continue

		attr = '%s.%s[%d]' % (rbsNode, attrName, upIdx)
		name = '%s_%s' % (targetName[0], attrName)
		_setAlias(attr, name)

def _createEyeLocators(rbsNode, lowerIdx):
	prfx = _getTargetNameFromIdx(rbsNode, lowerIdx)[0]
	
	# create locs or get existing ones
	eyelidLocList = cmds.ls(prfx + _eyelidLocSfx, transforms=True)
	eyeLocList = cmds.ls(prfx + _eyeLocSfx, transforms=True)
	eyeParentLocList = cmds.ls(prfx + _eyeParentLocSfx, transforms=True)
	headGrpList = cmds.ls(prfx + _headGrpSfx, transforms=True)
	
	eyelidLoc = eyelidLocList and eyelidLocList[0] or cmds.spaceLocator(n=prfx + _eyelidLocSfx)[0]
	eyeLoc = eyeLocList and eyeLocList[0] or cmds.spaceLocator(n=prfx + _eyeLocSfx)[0]
	eyeParentLoc = eyeParentLocList and eyeParentLocList[0] or cmds.spaceLocator(n=prfx + _eyeParentLocSfx)[0]
	headGrp = headGrpList and headGrpList[0] or cmds.group(em=True, n=prfx + _headGrpSfx)
	
	# make the hierarchy
	eyeLoc = _parent(eyeLoc, eyeParentLoc)
	eyeParentLoc = _parent(eyeParentLoc, headGrp)
	
	# colors
	eyelidLocShape = cmds.listRelatives(eyelidLoc, s=True, pa=True)[0]
	eyeLocShape = cmds.listRelatives(eyeLoc, s=True, pa=True)[0]
	eyeParentLocShape = cmds.listRelatives(eyeParentLoc, s=True, pa=True)[0]
	cmds.setAttr(eyelidLocShape + ".overrideEnabled", True)
	cmds.setAttr(eyelidLocShape + ".overrideColor", 17)
	cmds.setAttr(eyeLocShape + ".overrideEnabled", True)
	cmds.setAttr(eyeLocShape + ".overrideColor", 28)
	cmds.setAttr(eyeParentLocShape + ".localScale", 0.2, 0.2, 0.2)
	cmds.setAttr(eyeParentLocShape + ".overrideEnabled", True)
	cmds.setAttr(eyeParentLocShape + ".overrideColor", 29)
	
	# connect
	for idx in [lowerIdx, lowerIdx+1]:
		cmds.connectAttr('%s.worldMatrix' % eyelidLoc, '%s.it[%d].%s' % (rbsNode, idx, _targetAttrs[2]))
		cmds.connectAttr('%s.matrix' % eyeLoc, '%s.it[%d].%s' % (rbsNode, idx, _targetAttrs[3]))
		cmds.connectAttr('%s.matrix' % eyeParentLoc, '%s.it[%d].%s' % (rbsNode, idx, _targetAttrs[4]))

	# get the sub group
	subGrpList = cmds.ls(prfx + _eyelidGrpName, transforms=True)
	subGrp = subGrpList and subGrpList[0] or cmds.group(em=True, n=prfx + _eyelidGrpName)

	# get or create the top group
	locGrpList = cmds.ls(_locGrpName, transforms=True)
	locGrp = locGrpList and locGrpList[0] or cmds.group(em=True, n=_locGrpName)

	# parent to top group
	_parent(eyelidLoc, subGrp)
	_parent(headGrp, subGrp)
	_parent(subGrp, locGrp)

def _selectTab(prfx):
	tabNameList = cmds.tabLayout(_controls['tabLAY'], q=True, tli=True) or []
	if prfx in tabNameList:
		cmds.tabLayout(_controls['tabLAY'], e=True, sti=tabNameList.index(prfx)+1)

def _updateTabUI(rbsNode):
	"""Re-generate tabs, one per eye."""

	# delete all content
	content = cmds.tabLayout(_controls['tabLAY'], q=True, ca=True) or []
	for control in content:
		cmds.deleteUI(control)
	
	if not rbsNode:
		return
	
	content = []
	idxPrfxList = _getEyeIdxPrfxList(rbsNode)

	# for each eye, create content
	for lowerIdx, prfx in idxPrfxList:
		upperIdx = lowerIdx + 1
		
		# get info for enabling ui elements
		isBulgeEnabled = (lowerIdx+1) in _getAttrIdxList(rbsNode, _bulgeAttrs[0])
		isMirrorEnabled = len(_getAttrIdxList(rbsNode, _bulgeAttrs[0])) > 1
		connList = cmds.listConnections('%s.it[%d].%s' % (rbsNode, lowerIdx, _targetAttrs[0]), d=False)
		lowerGeo = connList and connList[0]
		lowerGeoData = bool(cmds.getAttr('%s.it[%d].%s' % (rbsNode, lowerIdx, _targetAttrs[0]), type=True))
		connList = cmds.listConnections('%s.it[%d].%s' % (rbsNode, lowerIdx, _targetAttrs[1]), d=False)
		lowerOppGeo = connList and connList[0]
		lowerOppGeoData = bool(cmds.getAttr('%s.it[%d].%s' % (rbsNode, lowerIdx, _targetAttrs[1]), type=True))
		connList = cmds.listConnections('%s.it[%d].%s' % (rbsNode, upperIdx, _targetAttrs[0]), d=False)
		upperGeo = connList and connList[0]
		upperGeoData = bool(cmds.getAttr('%s.it[%d].%s' % (rbsNode, upperIdx, _targetAttrs[0]), type=True))
		connList = cmds.listConnections('%s.it[%d].%s' % (rbsNode, upperIdx, _targetAttrs[1]), d=False)
		upperOppGeo = connList and connList[0]
		upperOppGeoData = bool(cmds.getAttr('%s.it[%d].%s' % (rbsNode, upperIdx, _targetAttrs[1]), type=True))
		connList = cmds.listConnections('%s.%s[%d]' % (rbsNode, _attrs[0], upperIdx), d=False)
		upperMainCtrl = connList and connList[0]
		upperMainCtrlData = bool(connList)
		connList = cmds.listConnections('%s.%s[%d]' % (rbsNode, _attrs[0], lowerIdx), d=False)
		lowerMainCtrl = connList and connList[0]
		lowerMainCtrlData = bool(connList)
		upperOffsetCtrls = []
		upperOffsetCtrlsData = []
		lowerOffsetCtrls = []
		lowerOffsetCtrlsData = []
		for attr in _offsetAttrs:
			connList = cmds.listConnections('%s.%s[%d]' % (rbsNode, attr, upperIdx), d=False)
			upperOffsetCtrls.append(connList and connList[0])
			upperOffsetCtrlsData.append(bool(connList))
			connList = cmds.listConnections('%s.%s[%d]' % (rbsNode, attr, lowerIdx), d=False)
			lowerOffsetCtrls.append(connList and connList[0])
			lowerOffsetCtrlsData.append(bool(connList))

		cmds.setParent(_controls['tabLAY'])

		# create tab layout
		eyeTab = cmds.formLayout()
		
		# add the remove target button
		rmSideBT = cmds.button(l='Remove %s' % prfx, ann='Remove shape group', c=cb(removeEyeCmd, rbsNode, lowerIdx))
		
		# upper shape
		cmds.setParent(eyeTab)
		f1 = cmds.frameLayout(l='Upper eyelid', borderStyle='etchedOut', mw=2, mh=2)
		cmds.columnLayout(adj=True)
		cmds.rowLayout(nc=4, adj=4, ct4=['both', 'both', 'both', 'both'], cl4=['center', 'center', 'center', 'left'], cw=[1, 120])
		cmds.button(l='Set upper closed', ann='Set upper lid closed shape', bgc=(0.4, 0.8, 0.4), c=cb(setLidFromSelectionCmd, rbsNode, upperIdx))
		cmds.button(l='Regen', ann='Regenerate shape', en=upperGeoData and not upperGeo, c=cb(regenCmd, rbsNode, upperIdx))
		cmds.separator(w=8, st='none')
		cmds.text(l=upperGeo or upperGeoData and '*STORED*' or '*MISSING*')
		cmds.setParent('..')
		cmds.rowLayout(nc=4, adj=4, ct4=['both', 'both', 'both', 'both'], cl4=['center', 'center', 'center', 'left'], cw=[1, 120])
		cmds.button(l='Set upper open', ann='Set upper lid open shape', bgc=(0.4, 0.7, 0.9), en=upperGeoData, c=cb(setLidFromSelectionCmd, rbsNode, upperIdx, True))
		cmds.button(l='Regen', ann='Regenerate shape', en=upperOppGeoData and not upperOppGeo, c=cb(regenCmd, rbsNode, upperIdx, True))
		cmds.separator(w=8, st='none')
		cmds.text(l=upperOppGeo or upperOppGeoData and '*STORED*' or '*OPTIONAL*')
		cmds.setParent('..')
		cmds.separator(h=8, st='none')

		# main upper control button
		cmds.rowLayout(nc=4, adj=4, ct4=['both', 'both', 'both', 'both'], cl4=['center', 'center', 'center', 'left'], cw=[1, 100])
		cmds.button(l='Set main control', ann='Set upper lid control', bgc=(0.7, 0.5, 0.9), en=upperGeoData, c=cb(setMainControlCmd, rbsNode, upperIdx), h=18)
		cmds.button(l='Select', ann='Select the assigned upper lid control', en=upperMainCtrlData, c=cb(selectMainControlCmd, rbsNode, upperIdx), h=18)
		cmds.separator(w=8, st='none')
		cmds.text(l=upperMainCtrl or '*MISSING*')
		cmds.setParent('..')

		for i, attr in enumerate(_offsetAttrs):
			cmds.rowLayout(nc=4, adj=4, ct4=['both', 'both', 'both', 'both'], cl4=['center', 'center', 'center', 'left'], cw=[1, 100])
			name = attr.replace('offset', '').upper()
			cmds.button(l='Set %s control' % name, ann='Set upper lid %s offset control' % name, en=upperGeoData, c=cb(setOffsetControlCmd, rbsNode, upperIdx, i), h=18)
			cmds.button(l='Select', ann='Select the assigned offset control', en=upperOffsetCtrlsData[i], c=cb(selectOffsetControlCmd, rbsNode, upperIdx, i), h=18)
			cmds.separator(w=8, st='none')
			cmds.text(l=upperOffsetCtrls[i] or '*OPTIONAL*')
			cmds.setParent('..')


		# lower shape
		cmds.setParent(eyeTab)
		f2 = cmds.frameLayout(l='Lower eyelid', borderStyle='etchedOut', mw=2, mh=2)
		cmds.columnLayout(adj=True)
		cmds.rowLayout(nc=4, adj=4, ct4=['both', 'both', 'both', 'both'], cl4=['center', 'center', 'center', 'left'], cw=[1, 120])
		cmds.button(l='Set lower closed', ann='Set lower lid closed shape', bgc=(0.4, 0.8, 0.4), c=cb(setLidFromSelectionCmd, rbsNode, lowerIdx))
		cmds.button(l='Regen', ann='Regenerate shape', en=lowerGeoData and not lowerGeo, c=cb(regenCmd, rbsNode, lowerIdx))
		cmds.separator(w=8, st='none')
		cmds.text(l=lowerGeo or lowerGeoData and '*STORED*' or '*MISSING*')
		cmds.setParent('..')
		cmds.rowLayout(nc=4, adj=4, ct4=['both', 'both', 'both', 'both'], cl4=['center', 'center', 'center', 'left'], cw=[1, 120])
		cmds.button(l='Set lower open', ann='Set lower lid open shape', bgc=(0.4, 0.7, 0.9), en=lowerGeoData, c=cb(setLidFromSelectionCmd, rbsNode, lowerIdx, True))
		cmds.button(l='Regen', ann='Regenerate shape', en=lowerOppGeoData and not lowerOppGeo, c=cb(regenCmd, rbsNode, lowerIdx, True))
		cmds.separator(w=8, st='none')
		cmds.text(l=lowerOppGeo or lowerOppGeoData and '*STORED*' or '*OPTIONAL*')
		cmds.setParent('..')
		cmds.separator(h=8, st='none')

		# main lower control button
		cmds.rowLayout(nc=4, adj=4, ct4=['both', 'both', 'both', 'both'], cl4=['center', 'center', 'center', 'left'], cw=[1, 100])
		cmds.button(l='Set main control', ann='Set lower lid control', bgc=(0.7, 0.5, 0.9), en=lowerGeoData, c=cb(setMainControlCmd, rbsNode, lowerIdx), h=18)
		cmds.button(l='Select', ann='Select the assigned lower lid control', en=lowerMainCtrlData, c=cb(selectMainControlCmd, rbsNode, lowerIdx), h=18)
		cmds.separator(w=8, st='none')
		cmds.text(l=lowerMainCtrl or '*MISSING*')
		cmds.setParent('..')

		for i, attr in enumerate(_offsetAttrs):
			cmds.rowLayout(nc=4, adj=4, ct4=['both', 'both', 'both', 'both'], cl4=['center', 'center', 'center', 'left'], cw=[1, 100])
			name = attr.replace('offset', '').upper()
			cmds.button(l='Set %s control' % name, ann='Set lower lid %s offset control' % name, en=lowerGeoData, c=cb(setOffsetControlCmd, rbsNode, lowerIdx, i), h=18)
			cmds.button(l='Select', ann='Select the assigned offset control', en=lowerOffsetCtrlsData[i], c=cb(selectOffsetControlCmd, rbsNode, lowerIdx, i), h=18)
			cmds.separator(w=8, st='none')
			cmds.text(l=lowerOffsetCtrls[i] or '*OPTIONAL*')
			cmds.setParent('..')

		# bulging
		cmds.setParent(eyeTab)
		f3 = cmds.frameLayout(l='Eye bulge', borderStyle='etchedOut', mw=2, mh=2)
		cmds.columnLayout(adj=True)
		cmds.rowLayout(nc=5, ct5=['both', 'both', 'both', 'both', 'both'], cl5=['center', 'center', 'center', 'center', 'left'])
		cmds.separator(w=8, st='none')
		cmds.checkBox(l='Enable', v=isBulgeEnabled, ofc=cb(setBulgeCmd, rbsNode, upperIdx, False), onc=cb(setBulgeCmd, rbsNode, upperIdx, True))
		cmds.separator(w=4, st='none')
		cmds.button(l='Paint bulge weights', ann='Paint bulge weights for %s eye' % prfx, en=isBulgeEnabled, c=cb(paintWeightsCmd, rbsNode, upperIdx))
		cmds.button(l='Mirror weights from...', ann='Copy and mirror bulge weights', en=isMirrorEnabled, c=cb(mirrorWeightsCmd, rbsNode, upperIdx))

		cmds.formLayout(eyeTab, e=True, attachForm=[(rmSideBT, 'top', 0), (rmSideBT, 'left', 0), (rmSideBT, 'right', 0), (f1, 'left', 0), (f1, 'right', 0), (f2, 'left', 0), (f2, 'right', 0), (f3, 'left', 0), (f3, 'right', 0), (f3, 'bottom', 0)],
		                attachControl=[(f1, 'top', 0, rmSideBT), (f2, 'top', 0, f1), (f3, 'top', 0, f2)])
		
		content.append((eyeTab, prfx))
	
	if content:
		cmds.tabLayout(_controls['tabLAY'], edit=True, tabLabel=content)

def _updateUI():
	"""Enable/disable buttons."""
	
	geo = _getGeoFromUI()
	rbsNode = geo and _getRbs(geo)
	
	idxList = rbsNode and _getEyeIdxList(rbsNode) or []
	anyShape = any([bool(cmds.getAttr('%s.it[%d].%s' % (rbsNode, idx, _targetAttrs[0]), type=True)) for idx in idxList])
	
	# enable/disable ui
	cmds.button(_controls['createBT'], e=True, en=bool(geo) and not bool(rbsNode))
	cmds.text(_controls['rbs'], e=True, l=rbsNode or '')
	cmds.button(_controls['addEyeBT'], e=True, en=bool(rbsNode))
	cmds.button(_controls['editMembBT'], e=True, en=bool(rbsNode))
	cmds.button(_controls['autoMembBT'], e=True, en=anyShape)
	cmds.button(_controls['computeDispBT'], e=True, en=anyShape)
	cmds.button(_controls['deleteBT'], e=True, en=bool(rbsNode))
	
	_updateTabUI(rbsNode)

def _disconnectTargetWeights(rbsNode, idx):
	"""Disconnects targetWeight elements."""

	# check incoming connections to targetWeight attr
	wAttrFull = '%s.it[%d].%s' % (rbsNode, idx, _wAttr)
	connList = cmds.listConnections(wAttrFull, d=False, p=True)

	if not connList:
		return

	# disconnect targetWeights
	cmds.disconnectAttr(connList[0], wAttrFull)

def _disconnectPaintWeights(rbsNode):
	"""Disconnects any outgoing connection from the paintable weights."""

	pAttr = '%s.weightList[0].weights' % rbsNode
	destConnList = cmds.listConnections(pAttr, s=False, p=True) or []
	for dest in destConnList:
		src = cmds.listConnections(dest, d=False, p=True)[0]
		cmds.disconnectAttr(src, dest)

def getGeoCmd():
	geo = _getSelectedShape('mesh')
	
	cmds.text(_controls['geo'], e=True, l=geo or '')
	
	_updateUI()

def createCmd():
	"""Create node."""
	
	geo = _getGeoFromUI()
	rbsNode = geo and _getRbs(geo)
	
	if rbsNode:
		_updateUI()
		return
	
	# create the rbs
	cmds.deformer(geo, typ=_rbsNodeName, foc=True)
	
	_updateUI()

def addEyeCmd():
	"""Adds new eyelid inputs."""
	
	geo = _getGeoFromUI()
	rbsNode = geo and _getRbs(geo)
	
	prfx = cmds.layoutDialog(t='Add eye', ui=lambda *x: _addEyeDialog(rbsNode))
	if len(prfx) > 1:
		return
	
	# find first available lower lid index
	miList = _getEyeIdxList(rbsNode)
	idx = 0
	while idx in miList or (idx+1) in miList:
		idx += 2
	
	lowerAttr = '%s.it[%d]' % (rbsNode, idx)
	upperAttr = '%s.it[%d]' % (rbsNode, idx+1)
	lowerName = '%s_lower' % prfx
	upperName = '%s_upper' % prfx
	
	# add lower and upper indices
	cmds.getAttr('%s.im' % lowerAttr)
	cmds.getAttr('%s.im' % upperAttr)

	# set the aliases for the inputTarget attributes (lower and upper)
	if cmds.aliasAttr(lowerAttr, q=True) != lowerName:
		_setAlias(lowerAttr, lowerName)
	if cmds.aliasAttr(upperAttr, q=True) != upperName:
		_setAlias(upperAttr, upperName)
	
	# create and connect locators
	_createEyeLocators(rbsNode, idx)
	
	# update tab ui
	_updateUI()
	_selectTab(prfx)

def paintWeightsCmd(rbsNode, upperIdx):
	wAttr = '%s.it[%d].%s' % (rbsNode, upperIdx, _wAttr)
	pAttr = '%s.weightList[0].weights' % rbsNode

	# disconnect
	_disconnectPaintWeights(rbsNode)
	
	# copy and connect
	cmds.connectAttr(wAttr, pAttr, f=True)
	cmds.getAttr(pAttr, mi=True)
	cmds.disconnectAttr(wAttr, pAttr)
	cmds.connectAttr(pAttr, wAttr, f=True)

	# paint tool
	obj = cmds.listRelatives(cmds.deformer(rbsNode, q=True, g=True), p=True, pa=True)[0]
	cmds.select(obj)
	cmds.setToolTo(cmds.artAttrCtx(oaa='%s.%s.weights' % (_rbsNodeName, rbsNode)))

def mirrorWeightsCmd(rbsNode, upperIdx):
	destIdx = upperIdx

	# get destination prefix
	destPrfx = _getTargetNameFromIdx(rbsNode, destIdx)[0]

	# ask for the source
	srcPrfx = cmds.layoutDialog(t='Mirror bulge weights', ui=lambda *x: _mirrorWeightsDialog(rbsNode, destPrfx))
	if len(srcPrfx) > 1:
		return

	# find the source index
	idxPrfxList = _getEyeIdxPrfxList(rbsNode)

	srcIdx = -1
	for lowerIdx, prfx in idxPrfxList:
		if prfx == srcPrfx:
			srcIdx = lowerIdx + 1
			break

	if srcIdx < 0:
		raise Exception, 'Cannot find the index of target %s' % srcPrfx

	# membership set
	objSetNode = _getMembershipSet(rbsNode)
	affectedVtxList = cmds.ls(cmds.sets(objSetNode, q=True) or [], fl=True)

	# find original shape
	obj = cmds.listRelatives(cmds.deformer(rbsNode, q=True, g=True), p=True, pa=True)[0]
	origShape = [s for s in cmds.listRelatives(obj, s=True, pa=True) if cmds.getAttr('%s.intermediateObject' % s)][0]

	# get the original point position
	origAffectedVtxList = ['%s%s' % (origShape, vtx[vtx.rindex('.'):]) for vtx in affectedVtxList]
	vtxCount = len(origAffectedVtxList)
	posList = cmds.xform(origAffectedVtxList, q=True, os=True, t=True)
	posList = [posList[i:i+3] for i in xrange(0, len(posList), 3)]

	# create a symmetry map (it stores the indices of the opposite vertices)
	cmds.progressBar('mainProgressBar', e=True, beginProgress=True, isInterruptable=False, status='Generating symmetry map...', maxValue=vtxCount)
	symmMap = [-1]*len(affectedVtxList)
	for i, pos in enumerate(posList):
		cmds.progressBar('mainProgressBar', e=True, step=1)
		# avoid doing the test twice for the opposite vertex
		if symmMap[i] != -1:
			continue

		oppIdx = -1
		minDistance = 1000000.0

		for j, otherPos in enumerate(posList):
			dist = (otherPos[0]+pos[0])**2 + (otherPos[1]-pos[1])**2 + (otherPos[2]-pos[2])**2
			if dist < minDistance:
				minDistance = dist
				oppIdx = j

		symmMap[i] = oppIdx
		symmMap[oppIdx] = i
	cmds.progressBar('mainProgressBar', e=True, endProgress=True)

	# disconnect paint weights
	_disconnectPaintWeights(rbsNode)

	srcAttr = '%s.it[%d].%s' % (rbsNode, srcIdx, _wAttr)
	destAttr = '%s.it[%d].%s' % (rbsNode, destIdx, _wAttr)
	pAttr = '%s.weightList[0].weights' % rbsNode

	# copy weights from source to paint
	cmds.connectAttr(srcAttr, pAttr, f=True)
	cmds.getAttr(pAttr, mi=True)
	cmds.disconnectAttr(srcAttr, pAttr)

	# connect paint to destination weights
	cmds.connectAttr(pAttr, destAttr, f=True)

	affectedWeightList = cmds.percent(rbsNode, affectedVtxList, q=True, v=True)

	# set weights
	cmds.progressBar('mainProgressBar', e=True, beginProgress=True, isInterruptable=False, status='Setting weights...', maxValue=vtxCount)
	for i, vtx in enumerate(affectedVtxList):
		cmds.progressBar('mainProgressBar', e=True, step=1)
		cmds.percent(rbsNode, vtx, v=affectedWeightList[symmMap[i]])
	cmds.progressBar('mainProgressBar', e=True, endProgress=True)

	# show the paint tool
	cmds.select(obj)
	cmds.setToolTo(cmds.artAttrCtx(oaa='%s.%s.weights' % (_rbsNodeName, rbsNode)))

def removeEyeCmd(rbsNode, lowerIdx):
	"""Removes lower and upper eyelid of the given side."""
	
	idxList = [lowerIdx, lowerIdx+1]
	
	attrList = _attrs + _bulgeAttrs + _blinkAttrs + _offsetInfluenceAttrs + _offsetAttrs
	
	for idx in idxList:
		# attrs in the inputTarget array
		if idx in _getEyeIdxList(rbsNode):
			_disconnectTargetWeights(rbsNode, idx)
			
			for attrName in _targetAttrs:
				attr = '%s.it[%d].%s' % (rbsNode, idx, attrName)
				_disconnectAndRemoveAttr(attr)
			_disconnectAndRemoveAttr('%s.it[%d]' % (rbsNode, idx), True)
		
		# channel box attrs
		for attrName in attrList:
			if idx in _getAttrIdxList(rbsNode, attrName):
				attr = '%s.%s[%d]' % (rbsNode, attrName, idx)
				_disconnectAndRemoveAttr(attr, True)
	
	_updateUI()

def editMembershipCmd():
	"""Membership tool."""
	
	geo = _getGeoFromUI()
	rbsNode = geo and _getRbs(geo)
	
	if rbsNode:
		cmds.select(rbsNode)
		cmds.setToolTo('setEditContext')
		sys.stdout.write('Use shift/ctrl to add/remove vertices from the deformer\n')
	
	_updateUI()

def autoMembershipCmd():
	geo = _getGeoFromUI()
	rbsNode = geo and _getRbs(geo)
	
	if not rbsNode:
		raise Exception, 'No %s found' % _rbsNodeName
	
	# orig shape coords
	origShape = [s for s in cmds.listRelatives(geo, s=True, pa=True) if cmds.getAttr('%s.intermediateObject' % s)][0]
	origCoords = cmds.xform('%s.vtx[*]' % origShape, q=True, os=True, t=True)
	vtxCount = cmds.polyEvaluate(origShape, v=True)
	
	tidxList = _getEyeIdxList(rbsNode)
	shapeList = []
	deleteList = []
	
	# get connected shapes or regen them if absent
	for tidx in tidxList:
		for i in [0, 1]:
			attr = '%s.it[%d].%s' % (rbsNode, tidx, _targetAttrs[i])
			connList = cmds.listConnections(attr, d=False)
			if connList:
				shapeList.append(connList[0])
			elif cmds.getAttr(attr, type=True):
				obj = regenCmd(rbsNode, tidx, i == 1)
				shapeList.append(obj)
				deleteList.append(obj)
	
	modIdxSet = set()
	
	for shape in shapeList:
		targetCoords = cmds.xform('%s.vtx[*]' % shape, q=True, os=True, t=True)
		for idx in xrange(vtxCount):
			i = idx*3
			if (abs(targetCoords[i]-origCoords[i]) > _autoMembTolerance) or (abs(targetCoords[i+1]-origCoords[i+1]) > _autoMembTolerance) or (abs(targetCoords[i+2]-origCoords[i+2]) > _autoMembTolerance):
				modIdxSet.add(idx)
	
	# delete any shape I created
	if deleteList:
		cmds.delete(deleteList)
	
	if len(modIdxSet) == 0:
		cmds.warning('No shape deltas found in %s. No point will be removed.' % geo)
		return
	
	# fill the set
	objSetNode = _getMembershipSet(rbsNode)
	cmds.sets('%s.vtx[*]' % geo, add=objSetNode)
	
	# remove from the set
	idxToRemSet = set(range(vtxCount)) - modIdxSet
	pListToRemove = ['%s.vtx[%d]' % (geo, idx) for idx in idxToRemSet]
	cmds.sets(pListToRemove, rm=objSetNode)
	
	# membership tool
	cmds.select(rbsNode)
	cmds.setToolTo('setEditContext')
	
	cmds.confirmDialog(t='Auto membership', m='Optimization complete.\nUsing %d of %d points.' % (len(modIdxSet), vtxCount))

def deleteCmd():
	"""Delete node."""
	
	geo = _getGeoFromUI()
	rbsNode = geo and _getRbs(geo)
	
	if rbsNode:
		cmds.delete(rbsNode)
	
	_updateUI()

def setLidFromSelectionCmd(rbsNode, idx, opposite=False):
	"""Adds an eyelid target."""
	
	lidGeo = _getSelectedShape('mesh')
	
	if not lidGeo:
		raise Exception, 'Please select a polygon mesh'
	
	if _getRbs(lidGeo):
		raise Exception, 'The main geometry cannot be used as a shape'
	
	targetName = _getTargetNameFromIdx(rbsNode, idx)
	
	if idx == -1:
		raise Exception, 'Input target %s does not exist, please refresh GUI' % targetName
	
	# make the connection if not yet done
	srcAttr = '%s.outMesh' % lidGeo
	destAttr = '%s.it[%d].%s' % (rbsNode, idx, _targetAttrs[int(opposite)])
	connections = cmds.listConnections(destAttr, d=False) or []
	if lidGeo in connections:
		cmds.warning('The geometry you selected is already connected to %s' % destAttr)
		return
	
	# connect geometry
	cmds.connectAttr(srcAttr, destAttr, f=True)
	
	if not opposite:
		# set default values
		for i, attr in enumerate(_attrs):
			cmds.setAttr('%s.%s[%d]' % (rbsNode, attr, idx), _defAttrValues[i])
		
		for i, attr in enumerate(_offsetAttrs):
			cmds.getAttr('%s.%s[%d]' % (rbsNode, attr, idx))

		for i, attr in enumerate(_offsetInfluenceAttrs):
			upIdx = idx + 1 - idx%2
			# don't set it if it has already been set by the other lid (since it's a common value)
			if not upIdx in _getAttrIdxList(rbsNode, attr):
				cmds.setAttr('%s.%s[%d]' % (rbsNode, attr, upIdx), _defOffsetInfluenceValues[i])

		# just for odd indices (upper lid) set the blink attribute
		if idx % 2 == 1:
			for attr in _blinkAttrs:
				cmds.setAttr('%s.%s[%d]' % (rbsNode, attr, idx), 0.0)

		# set aliases
		_setAttrAliases(rbsNode, idx)
	
	_updateUI()
	_selectTab(targetName[0])

def setOffsetControlCmd(rbsNode, idx, side):
	sel = cmds.ls(sl=True, transforms=True)
	if not sel:
		raise Exception, 'Please select the desired control'

	ctrl = sel[0]

	# check if this object is already connected to the attribute
	destAttr = '%s.%s[%d]' % (rbsNode, _offsetAttrs[side], idx)
	connList = cmds.listConnections(destAttr, d=False) or []

	if ctrl in connList:
		cmds.warning('The object you selected is already connected to %s' % destAttr)
		return

	# connect it
	cmds.connectAttr('%s.t' % ctrl, destAttr, f=True)

	# set alias (in case I set the control before the shape)
	_setAttrAliases(rbsNode, idx)

	# update tab ui
	targetName = _getTargetNameFromIdx(rbsNode, idx)
	_updateTabUI(rbsNode)
	_selectTab(targetName[0])

def selectOffsetControlCmd(rbsNode, idx, side):
	ctrl = cmds.listConnections('%s.%s[%d]' % (rbsNode, _offsetAttrs[side], idx), d=False)[0]
	cmds.select(ctrl)

def setMainControlCmd(rbsNode, idx):
	# get selection
	sel = cmds.ls(sl=True, transforms=True)
	if not sel:
		raise Exception, 'Please select the desired control'

	idxList = _getEyeIdxList(rbsNode)
	if not idx in idxList:
		raise Exception, 'Eye index %d does not exist' % idx

	ctrl = sel[0]

	attrPairs = [['ty', _attrs[0]], ['tx', _attrs[1]]]

	# connect translation attrs
	for srcAttr, destAttr in attrPairs:
		# check if this object is already connected to the attribute
		dest = '%s.%s[%d]' % (rbsNode, destAttr, idx)
		connList = cmds.listConnections(dest, d=False) or []
		if not ctrl in connList:
			src = '%s.%s' % (ctrl, srcAttr)
			cmds.connectAttr(src, dest, f=True)
			sys.stdout.write('%s -> %s\n' % (src, dest))

	# user defined attributes
	newAttrPairs = [[_attrs[2], _attrs[2], 1.0]]

	# if it's upper, add the blink attr
	if idx % 2 == 1:
		newAttrPairs.append([_blinkAttrs[0], _blinkAttrs[0], 0.0])
		newAttrPairs.append([_blinkAttrs[1], _blinkAttrs[1], 0.0])

	# user defined attrs
	udAttrs = cmds.listAttr(ctrl, k=True, ud=True) or []

	# create misc attr
	if not udAttrs:
		cmds.addAttr(ctrl, ln='misc', at='enum', en=' ', k=True)
		cmds.setAttr('%s.misc' % ctrl, l=True)

	for srcAttr, destAttr, defVal in newAttrPairs:
		# create attr if needed
		if not srcAttr in udAttrs:
			cmds.addAttr(ln=srcAttr, at='double', min=0.0, max=1.0, dv=defVal, k=True)

		# check if this object is already connected to the attribute
		dest = '%s.%s[%d]' % (rbsNode, destAttr, idx)
		connList = cmds.listConnections(dest, d=False) or []
		if not ctrl in connList:
			src = '%s.%s' % (ctrl, srcAttr)
			cmds.connectAttr(src, dest, f=True)
			sys.stdout.write('%s -> %s\n' % (src, dest))

	# update tab ui
	targetName = _getTargetNameFromIdx(rbsNode, idx)
	_updateTabUI(rbsNode)
	_selectTab(targetName[0])

def selectMainControlCmd(rbsNode, idx):
	ctrl = cmds.listConnections('%s.%s[%d]' % (rbsNode, _attrs[0], idx), d=False)[0]
	cmds.select(ctrl)

def regenCmd(rbsNode, idx, opposite=False):
	"""Regenerates geometry from rbs shape."""
	
	attr = '%s.it[%d].%s' % (rbsNode, idx, _targetAttrs[int(opposite)])
	obj = cmds.listRelatives(cmds.createNode('mesh'), p=True, pa=True)[0]
	cmds.connectAttr(attr, '%s.inMesh' % obj)
	cmds.delete(obj, ch=True)
	cmds.connectAttr('%s.outMesh' % obj, attr, f=True)
	cmds.sets(obj, fe='initialShadingGroup')
	
	targetName = _getTargetNameFromIdx(rbsNode, idx)
	if targetName:
		obj = cmds.rename(obj, '%s_%s' % (targetName, opposite and 'open' or 'closed'))
	
	cmds.select(obj)
	
	_updateTabUI(rbsNode)
	_selectTab(targetName[0])
	
	return obj

def setBulgeCmd(rbsNode, upperIdx, enabled):
	"""Enables/disables bulge deformation."""
	
	targetName = _getTargetNameFromIdx(rbsNode, upperIdx)

	if enabled:
		# set def values
		for i, attr in enumerate(_bulgeAttrs):
			cmds.setAttr('%s.%s[%d]' % (rbsNode, attr, upperIdx), _defBulgeValues[i])
		_setAttrAliases(rbsNode, upperIdx)
	else:
		for attr in _bulgeAttrs:
			_disconnectAndRemoveAttr('%s.%s[%d]' % (rbsNode, attr, upperIdx), True)
	
	_updateTabUI(rbsNode)
	_selectTab(targetName[0])

def computeDispCmd():
	"""Forces recomputing the max displacement values."""

	geo = _getGeoFromUI()
	rbsNode = geo and _getRbs(geo)

	if rbsNode:
		cmds.setAttr('%s.%s' % (rbsNode, _computeDispAttr), 0)

def helpCmd():
	webbrowser.open("http://www.paolodominici.com/products/zvradialblendshape/#help")

def zvRadialBlendShape():
	# load plugin
	if not cmds.pluginInfo(_rbsNodeName, q=True, l=True):
		cmds.loadPlugin(_rbsNodeName)
	
	# make attribute paintable
	cmds.makePaintable(_rbsNodeName, 'weights', attrType='multiFloat', sm='deformer')
	
	# create window
	winName = 'ZvRadialBlendShapeWin'
	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName, window=True)

	cmds.window(winName, title='%s %s' % (__product__, __version__))
	
	mainLAY = cmds.formLayout()

	# geometry
	f1 = cmds.frameLayout(l='Geometry', borderStyle='etchedOut', mw=2, mh=2)
	cmds.columnLayout(adj=True)
	cmds.rowLayout(nc=3, adj=3, ct3=['both', 'both', 'both'], cl3=['center', 'center', 'left'], cw=[1, 120])
	cmds.button(l='Get geometry', ann='Refresh UI using selected geometry', c=cb(getGeoCmd))
	cmds.separator(w=8, st='none')
	geoTXT = cmds.text(l='')
	cmds.setParent(f1)
	cmds.rowLayout(nc=3, adj=3, ct3=['both', 'both', 'both'], cl3=['center', 'center', 'left'], cw=[1, 120])
	createBT = cmds.button(l='Create deformer', ann='Create Radial Blend Shape node', c=cb(createCmd))
	cmds.separator(w=8, st='none')
	rbsTXT = cmds.text(l='')
	
	# eyes
	cmds.setParent(mainLAY)
	f2 = cmds.frameLayout(l='Eyes', borderStyle='etchedOut', mw=2, mh=2)
	eyeFormLAY = cmds.formLayout(nd=20)
	addEyeBT = cmds.button(l='Add...', ann='Add shape group', c=cb(addEyeCmd))
	tabs = cmds.tabLayout(innerMarginWidth=2, innerMarginHeight=2)
	cmds.formLayout(eyeFormLAY, e=True,
	                attachForm=[(addEyeBT, 'top', 0), (addEyeBT, 'left', 0), (addEyeBT, 'right', 0), (tabs, 'left', 0), (tabs, 'right', 0), (tabs, 'bottom', 0)],
	                attachControl=[(tabs, 'top', 4, addEyeBT)])
	
	# tools
	cmds.setParent(mainLAY)
	f3 = cmds.frameLayout(l='Tools', borderStyle='etchedOut', mw=2, mh=2)
	cmds.columnLayout(adj=True, rs=2)
	
	membLAY = cmds.formLayout(nd=20)
	editMembBT = cmds.button(l='Edit membership', ann='Edit affected vertices', c=cb(editMembershipCmd))
	autoMembBT = cmds.button(l='Auto membership', ann='Optimize affected vertices', c=cb(autoMembershipCmd))
	cmds.formLayout(membLAY, e=True, attachForm=[(editMembBT, 'top', 0), (editMembBT, 'left', 0), (editMembBT, 'bottom', 0), (autoMembBT, 'top', 0), (autoMembBT, 'right', 0), (autoMembBT, 'bottom', 0)],
	                attachPosition=[(editMembBT, 'right', 1, 10), (autoMembBT, 'left', 1, 10)])
	
	cmds.setParent('..')
	computeDispBT = cmds.button(l='Compute displacements', ann='Compute maximum displacements for all shapes.\nThis must be done after a shape edit to make sure the offset controls work properly.', c=cb(computeDispCmd))
	deleteBT = cmds.button(l='Delete deformer', ann='Remove the Radial Blend Shape node attached to this geometry', c=cb(deleteCmd))
	cmds.button(l='Help', ann='Online documentation', bgc=(0.9, 0.8, 0.4), c=cb(helpCmd))

	cmds.formLayout(mainLAY, e=True,
	                attachForm=[(f1, 'top', 0), (f1, 'left', 0), (f1, 'right', 0), (f2, 'left', 0), (f2, 'right', 0), (f3, 'left', 0), (f3, 'right', 0), (f3, 'bottom', 0)],
	                attachControl=[(f2, 'top', 10, f1), (f2, 'bottom', 10, f3)])
	
	# control dict
	_controls['geo'] = geoTXT
	_controls['rbs'] = rbsTXT
	_controls['createBT'] = createBT
	_controls['addEyeBT'] = addEyeBT
	_controls['tabLAY'] = tabs
	_controls['editMembBT'] = editMembBT
	_controls['autoMembBT'] = autoMembBT
	_controls['deleteBT'] = deleteBT
	_controls['computeDispBT'] = computeDispBT

	_updateUI()
	
	# show window
	cmds.showWindow(winName)
	cmds.window(winName, edit=True, widthHeight=(320, 750))

	sys.stdout.write("%s %s          %s\n" % (__product__, __version__, __author__))

##
# TODO sovragruppi