'''ZV Radial Blend Shape

Usage:
import ZvRadialBlendShape
ZvRadialBlendShape.ZvRadialBlendShape()
'''

__author__ = 'Paolo Dominici (paolodominici@gmail.com)'
__version__ = '1.0'
__date__ = '2010/06/06'
__copyright__ = 'Copyright (c) 2010 Paolo Dominici'

import sys, webbrowser, re
from maya import cmds, mel

_rbsNodeName = 'radialBlendShape'
_isQt = not cmds.about(version=True).split()[0] in ['8.5', '2008', '2009', '2010']
_controls = {}
_unnamed = '<unnamed>'

_rbsAttrs = ('blend', 'twist', 'curvature')
_itAttr = 'inputTarget'
_imshAttr = 'inMesh'
_imatAttr = 'inMatrix'
_wAttr = 'targetWeights'
_paintableAttr = 'radialWeights'
_paintableParentAttr = 'radialWeightList'

_nameSfx = ('_B', '_T', '_C')
_locSfx = '_CNT'

def cb(func, *args):
	return '%s.%s(%s)' % (func.__module__, func.__name__, ', '.join([repr(s) for s in args]))

def _getRBS(obj):
	rbsNodeList = [s for s in cmds.listHistory(obj, pdo=True, il=2) or [] if cmds.nodeType(s) == _rbsNodeName]
	return rbsNodeList and rbsNodeList[0] or None

def _getSelectedMeshes():
	'''Get polygon meshes from selection.'''
	
	sel = cmds.ls(sl=True, transforms=True)
	
	meshes = []
	for s in sel:
		shapes = cmds.listRelatives(s, s=True)
		if shapes and cmds.nodeType(shapes[0]) == 'mesh':
			meshes.append(s)

	return meshes

def _getSelectedTarget():
	'''Return (rbsNode, targetIdx, targetName)'''
	
	obj = _getActiveObj()
	if not obj:
		return (None, None, None, None)
	
	rbsNode = _getRBS(obj)
	if not rbsNode:
		return (obj, None, None, None)
	
	selTslIdx = cmds.textScrollList(_controls['targets'], q=True, sii=True)
	if not selTslIdx:
		return (obj, rbsNode, None, None)
	
	targetIdx = _getTargetIndices(rbsNode)[selTslIdx[0] - 1]
	targetName = _getTargetNames(rbsNode, targetIdx)
	
	return (obj, rbsNode, targetIdx, targetName)

def _getTargetIndices(rbsNode):
	return cmds.getAttr('%s.%s' % (rbsNode, _rbsAttrs[0]), mi=True) or []

def _getTargetNames(rbsNode, idx=-1):
	if idx == -1:
		idxList = _getTargetIndices(rbsNode)
		return [_getTargetNames(rbsNode, i) for i in idxList]
	
	alias = cmds.aliasAttr('%s.%s[%d]' % (rbsNode, _rbsAttrs[0], idx), q=True)
	
	if not alias:
		return _unnamed
	
	elif alias.endswith(_nameSfx[0]):
		return alias[:-len(_nameSfx[0])]
	
	return alias

def _setTargetName(rbsNode, idx, name):
	# assicurati dell'unicita' del nome
	if name in _getTargetNames(rbsNode):
		# cerca un eventuale numero alla fine del nome
		mo = re.search('\d+$', name)
		
		if mo:
			numStr = mo.group()
			prefix = name[:-len(numStr)]
		else:
			numStr = '0'
			prefix = name
		
		return _setTargetName(rbsNode, idx, '%s%d' % (prefix, int(numStr)+1))
	
	for i in range(len(_rbsAttrs)):
		cmds.aliasAttr('%s%s' % (name, _nameSfx[i]), '%s.%s[%d]' % (rbsNode, _rbsAttrs[i], idx))
	
	return name

def _getActiveObj():
	label = cmds.frameLayout(_controls['form'], q=True, l=True)
	brIdx = label.find('[')
	if brIdx < 0:
		return None
	
	obj = label[brIdx+1:-1]
	return cmds.objExists(obj) and obj or None

def _getLocatorName(targetName):
	return targetName + _locSfx

def renameTargetCmd():
	obj, rbsNode, targetIdx, targetName = _getSelectedTarget()
	
	if not targetName:
		return
	
	if cmds.promptDialog(title='Rename target', message='Enter Name:', text=targetName!=_unnamed and targetName or '', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel') == 'OK':
		newName = cmds.promptDialog(query=True, text=True).strip()
		mo = re.match('\w', newName)
		if not mo:
			cmds.confirmDialog(title='Rename target', message='The name you entered is not valid', button=['OK'])
			return

		if newName == targetName:
			return
		
		_setTargetName(rbsNode, targetIdx, newName)
		
		lastSelIdx = cmds.textScrollList(_controls['targets'], q=True, sii=True)
		refreshCmd(obj)
		cmds.textScrollList(_controls['targets'], e=True, sii=lastSelIdx)

def regenerateTargetCmd():
	obj, rbsNode, targetIdx, targetName = _getSelectedTarget()
	
	if not targetName:
		return

	meshAttr = '%s.%s[%d].%s' % (rbsNode, _itAttr, targetIdx, _imshAttr)
	matAttr = '%s.%s[%d].%s' % (rbsNode, _itAttr, targetIdx, _imatAttr)
	
	meshConn = cmds.listConnections(meshAttr, d=False)
	matConn = cmds.listConnections(matAttr, d=False)
	
	# crea la mesh
	if not meshConn:
		shape = cmds.createNode('mesh')
		transform = cmds.listRelatives(shape, p=True, pa=True)[0]
		cmds.connectAttr(meshAttr, '%s.inMesh' % shape)
		target = cmds.duplicate(transform)[0]
		cmds.delete(transform)
		cmds.sets(target, fe='initialShadingGroup')
		cmds.connectAttr('%s.worldMesh[0]' % target, meshAttr, f=True)
		target = cmds.rename(target, targetName)
	else:
		target = meshConn[0]
	
	# crea il locator
	if not matConn:
		loc = cmds.spaceLocator(n=_getLocatorName(targetName))[0]
		cmds.xform(loc, m=cmds.getAttr(matAttr), ws=True)
		cmds.connectAttr('%s.worldMatrix' % loc, matAttr)
	
	cmds.select(target)
	
	# messaggio
	if not meshConn or not matConn:
		sys.stdout.write('%s regenerated\n' % targetName)
	else:
		sys.stdout.write('%s is already connected\n' % targetName)

def paintWeightsCmd():
	obj, rbsNode, targetIdx, targetName = _getSelectedTarget()
	
	if not targetName:
		return
	
	wAttr = ('%s.%s[%d].%s' % (rbsNode, _itAttr, targetIdx, _wAttr)) + '[%d]'
	pAttr = ('%s.%s[0].%s' % (rbsNode, _paintableParentAttr, _paintableAttr)) + '[%d]'
	
	# disconnetti l'attr paintabile
	destConnList = cmds.listConnections('%s.%s[0].%s' % (rbsNode, _paintableParentAttr, _paintableAttr), s=False, p=True) or []
	for i in xrange(len(destConnList)):
		cmds.disconnectAttr(pAttr % i, destConnList[i])
	
	# copia i pesi sull'attr paintabile e connetti l'attr paintabile sui targetWeights
	data = cmds.getAttr('%s.%s[%d].%s' % (rbsNode, _itAttr, targetIdx, _wAttr))[0]
	for i in xrange(len(data)):
		cmds.setAttr(pAttr % i, data[i])
		cmds.connectAttr(pAttr % i, wAttr % i)
	
	# spennella
	cmds.select(obj)
	mel.eval('artAttrToolScript 3 "";artSetToolAndSelectAttr("artAttrCtx", "%s.%s.%s");' % (_rbsNodeName, rbsNode, _paintableAttr))

def removeTargetCmd():
	obj, rbsNode, targetIdx, targetName = _getSelectedTarget()
	
	if not targetName:
		return
	
	# store selection
	lastSel = cmds.ls(sl=True)
	cmds.select(cl=True)
	
	attrList = ['%s.%s[%d]' % (rbsNode, attr, targetIdx) for attr in _rbsAttrs] + ['%s.%s[%d]' % (rbsNode, _itAttr, targetIdx)]

	# rimuovi alias
	for attr in attrList[:-1]:
		alias = cmds.ls(attr)[0]
		if not '[' in alias:
			cmds.aliasAttr(alias, rm=True)
	
	for attr in attrList:
		cmds.removeMultiInstance(attr, b=True)
	
	# restore selection
	cmds.select(lastSel or None)
	
	refreshCmd(obj)

def selectTargetCmd():
	'''Select a target when double-clicking the item.'''
	
	obj, rbsNode, targetIdx, targetName = _getSelectedTarget()
	
	if not targetName:
		return
	
	conn = cmds.listConnections('%s.%s[%d].%s' % (rbsNode, _itAttr, targetIdx, _imshAttr), d=False)
	if conn:
		cmds.select(conn[0])

def addTargetCmd():
	obj, rbsNode, targetIdx, targetName = _getSelectedTarget()
	
	if not obj:
		return
	
	vtxCount = cmds.polyEvaluate(obj, v=True)
	
	sel = _getSelectedMeshes()
	
	targetsToAdd = []
	# verifica se gli oggetti selezionati sono target validi
	for s in sel:
		# verifica se e' uno dei target esistenti
		if rbsNode:
			conn = cmds.listConnections('%s.worldMesh' % s, s=False) or []
			if rbsNode in conn:
				sys.stdout.write('%s is already a target\n' % s)
				continue
		
		# verifica se e' l'oggetto deformato
		if s == obj:
			sys.stdout.write('%s is not a valid target\n' % s)
			continue

		# verifica il numero di vertici
		if cmds.polyEvaluate(s, v=True) != vtxCount:
			sys.stdout.write('%s has different number of vertices\n' % s)
			continue
		
		targetsToAdd.append(s)
	
	# se non sono validi mostra messaggio
	if not targetsToAdd:
		cmds.confirmDialog(title='Add target', message='Please select one or more targets', button=['OK'])
		return
	
	# se non esiste crea il nodo
	if not rbsNode:
		rbsNode = cmds.deformer(obj, typ=_rbsNodeName, foc=True)[0]

	# aggiungi i target
	locList = []
	allIndices = _getTargetIndices(rbsNode)
	targetIdx = allIndices and (allIndices[-1]+1) or 0
	for target in targetsToAdd:
		# connetti il target
		cmds.connectAttr('%s.worldMesh[0]' % target, '%s.%s[%d].%s' % (rbsNode, _itAttr, targetIdx, _imshAttr))
		for attr in _rbsAttrs:
			cmds.setAttr('%s.%s[%d]' % (rbsNode, attr, targetIdx), 0.0)
		
		# setta il nome
		targetName = _setTargetName(rbsNode, targetIdx, target)
		
		# crea il locator
		loc = cmds.spaceLocator(n=_getLocatorName(targetName))[0]
		cmds.connectAttr('%s.worldMatrix' % loc, '%s.%s[%d].%s' % (rbsNode, _itAttr, targetIdx, _imatAttr))
		locList.append(loc)
		
		# setta i pesi
		wAttr = ('%s.%s[%d].%s' % (rbsNode, _itAttr, targetIdx, _wAttr)) + '[%d]'
		for i in xrange(vtxCount):
			cmds.setAttr(wAttr % i, 1.0)
		
		targetIdx += 1
	
	refreshCmd(obj)
	cmds.textScrollList(_controls['targets'], e=True, sii=cmds.textScrollList(_controls['targets'], q=True, ni=True))
	cmds.select(locList)

def editMembershipCmd():
	obj, rbsNode, targetIdx, targetName = _getSelectedTarget()
	
	if not rbsNode:
		return
	
	cmds.select(rbsNode)
	cmds.setToolTo('setEditContext')
	sys.stdout.write('shift/ctrl select to add/remove vertices from the deformer\n')

def helpCmd():
	webbrowser.open("http://www.paolodominici.com/products/zvradialblendshape/#help")

def closeWindowCmd(winName):
	cmds.deleteUI(winName, window=True)

def _enableUI():
	items = cmds.textScrollList(_controls['targets'], q=True, ai=True)
	anyItem = bool(items)
	validObj = bool(_getActiveObj())
	
	cmds.button(_controls['add'], e=True, en=validObj)
	for s in ['rename', 'remove', 'regenerate', 'paint', 'membership']:
		cmds.button(_controls[s], e=True, en=anyItem)

def refreshCmd(obj=None):
	if not obj:
		sel = _getSelectedMeshes()
		obj = sel and sel[0] or None
	
	# nome oggetto selezionato
	cmds.frameLayout(_controls['form'], e=True, l='Geometry:   %s' % (obj and ('[%s]' % obj) or 'None'))
	cmds.frameLayout(_controls['form'], e=True, lv=False)
	cmds.frameLayout(_controls['form'], e=True, lv=True)

	
	# remove all
	cmds.textScrollList(_controls['targets'], e=True, ra=True)
	
	if obj:
		# nodi rbs nella selezione
		rbsNode = _getRBS(obj)
		
		if rbsNode:
			nameList = _getTargetNames(rbsNode)
			if nameList:
				cmds.textScrollList(_controls['targets'], e=True, a=nameList, sii=1)

	_enableUI()

def ZvRadialBlendShape():
	if not cmds.pluginInfo(_rbsNodeName, q=True, l=True):
		cmds.loadPlugin(_rbsNodeName)
	
	# make the attr paintable
	cmds.makePaintable(_rbsNodeName, _paintableAttr, attrType='multiFloat', sm='deformer')
	
	prfx = __name__ + '.'
	
	winName = 'ZvRadialBlendShapeWin'
	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName, window=True)
	
	cmds.window(winName, title='ZV Radial Blend Shape ' + __version__)
	tabs = cmds.tabLayout(innerMarginWidth=2, innerMarginHeight=2)
	
	# main tab
	rbsTab = cmds.formLayout()
	f1 = cmds.frameLayout(l='Geometry:   None', borderStyle='etchedOut', mw=2, mh=2)
	targetForm = cmds.formLayout(nd=30)
	
	rfrBT = cmds.button(l='Get geometry', c=cb(refreshCmd))
	targetTSL = cmds.textScrollList(dcc=cb(selectTargetCmd))
	addBT = cmds.button(l='Add', c=cb(addTargetCmd))
	renBT = cmds.button(l='Rename', c=cb(renameTargetCmd))
	remBT = cmds.button(l='Remove', c=cb(removeTargetCmd))
	
	cmds.formLayout(targetForm, e=True,\
	                attachForm=[(rfrBT, 'top', 0), (rfrBT, 'left', 0), (rfrBT, 'right', 0), (targetTSL, 'left', 0), (targetTSL, 'right', 0), (addBT, 'left', 0), (remBT, 'right', 0), (addBT, 'bottom', 0), (renBT, 'bottom', 0), (remBT, 'bottom', 0)],\
	                attachControl=[(targetTSL, 'top', 2, rfrBT), (targetTSL, 'bottom', 2, addBT)],\
	                attachPosition=[(addBT, 'right', 1, 10), (renBT, 'left', 1, 10), (renBT, 'right', 1, 20), (remBT, 'left', 1, 20)])
	
	cmds.setParent(rbsTab)
	f2 = cmds.frameLayout(l='Tools', borderStyle='etchedOut', mw=2, mh=2)
	cmds.columnLayout(adj=True, rs=2)
	regenBT = cmds.button(l='Regenerate target', c=cb(regenerateTargetCmd))
	paintBT = cmds.button(l='Paint weights', c=cb(paintWeightsCmd))
	membBT = cmds.button(l='Edit membership', c=cb(editMembershipCmd))
	
	cmds.formLayout(rbsTab, e=True,\
	                attachForm=((f1, 'top', 0), (f1, 'left', 0), (f1, 'right', 0), (f2, 'bottom', 0), (f2, 'left', 0), (f2, 'right', 0)),\
	                attachControl=((f1, 'bottom', 20, f2)))
	
	
	# help tab
	cmds.setParent(tabs)
	helpTab = cmds.formLayout(nd=30)
	helpBT = cmds.button(l='Online Help', height=28, c=cb(helpCmd))
	closeBT = cmds.button(l='Close', height=28, c=cb(closeWindowCmd, winName))
	cmds.formLayout(helpTab, e=True, attachForm=[(closeBT, 'left', 2), (closeBT, 'right', 2), (closeBT, 'bottom', 2), (helpBT, 'top', 80)],\
					attachPosition=[(helpBT, 'left', 0, 8), (helpBT, 'right', 0, 22)])
	
	cmds.tabLayout(tabs, edit=True, tabLabel=((rbsTab, 'Create/Edit'), (helpTab, 'Help')), sti=1)
	
	# control dict
	_controls['add'] = addBT
	_controls['rename'] = renBT
	_controls['remove'] = remBT
	_controls['targets'] = targetTSL
	_controls['form'] = f1
	_controls['regenerate'] = regenBT
	_controls['paint'] = paintBT
	_controls['membership'] = membBT
	
	_enableUI()
	cmds.showWindow(winName)
	cmds.window(winName, edit=True, widthHeight=(280, 350))
	
	sys.stdout.write("ZV Radial Blend Shape %s          http://www.paolodominici.com          paolodominici@gmail.com\n" % __version__)

