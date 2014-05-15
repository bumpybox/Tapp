import os

from PySide import QtGui
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

from .resources import dialog as dialog


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class Window(QtGui.QMainWindow, dialog.Ui_MainWindow):

    def __init__(self, parent=maya_main_window()):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        self.modify_dialog()

        self.create_connections()

    def modify_dialog(self):

        pass

    def create_connections(self):

        self.create_pushButton.released.connect(self.create_pushButton_released)
        self.delete_pushButton.released.connect(self.delete_pushButton_released)
        self.help_pushButton.released.connect(self.help_pushButton_released)

    def sphereDist(self):
        #create nodes
        sph = cmds.polySphere(ch=True, name='spherePreview_geo')

        edgeGroup = cmds.group(empty=True, name='spherePreview_group')

        dist = cmds.createNode('distanceBetween')

        #setup group
        cmds.move(0, 0, 1, edgeGroup)

        #setup sphere
        cmds.connectAttr('%s.worldMatrix' % sph[0], '%s.inMatrix1' % dist)

        cmds.connectAttr('%s.worldMatrix' % edgeGroup, '%s.inMatrix2' % dist)

        cmds.connectAttr('%s.distance' % dist, '%s.radius' % sph[1])

        #create metaData
        meta = cmds.shadingNode('network', asUtility=True,
                                name='meta_spherePreview')
        cmds.addAttr(meta, longName='type', dataType='string')
        cmds.setAttr('%s.type' % meta, 'spherePreview', type='string')
        cmds.addAttr(meta, longName='createJoints', dataType='string')
        cmds.addAttr(meta, longName='sphere', attributeType='message')
        cmds.addAttr(meta, longName='group', attributeType='message')

        cmds.addAttr(sph[0], longName='metaParent', attributeType='message')
        cmds.addAttr(edgeGroup, longName='metaParent', attributeType='message')
        cmds.addAttr(dist, longName='metaParent', attributeType='message')

        cmds.connectAttr('%s.message' % meta, '%s.metaParent' % sph[0])
        cmds.connectAttr('%s.message' % meta, '%s.metaParent' % edgeGroup)
        cmds.connectAttr('%s.message' % meta, '%s.metaParent' % dist)
        cmds.connectAttr('%s.message' % sph[0], '%s.sphere' % meta)
        cmds.connectAttr('%s.message' % edgeGroup, '%s.group' % meta)

        #return
        return (sph[0], edgeGroup, meta)

    def create_pushButton_released(self):
        selCount = len(cmds.ls(sl=True))

        #zero selected
        if selCount == 0:
            #create locator
            loc = cmds.spaceLocator(name='spherePreview_loc')[0]

            #create sphere
            nodes = self.sphereDist()

            #setup sphere
            cmds.pointConstraint(loc, nodes[1])

            #setup loc
            cmds.move(0, 0, 1, loc)

            #attach metaData
            cmds.addAttr(loc, longName='metaParent', attributeType='message')

            cmds.connectAttr('%s.message' % nodes[2], '%s.metaParent' % loc)

            cmds.setAttr('%s.createJoints' % nodes[2], 'true', type='string')

        #one item selected
        if selCount == 1:
            #getting selection
            sel = cmds.ls(sl=True)[0]

            #create locator
            loc = cmds.spaceLocator(name='spherePreview_loc')[0]

            #create sphere
            nodes = self.sphereDist()

            #setup sphere
            cmds.pointConstraint(loc, nodes[1])

            cmds.delete(cmds.pointConstraint(sel, nodes[0]))

            #setup loc
            cmds.delete(cmds.pointConstraint(sel, loc))

            cmds.move(0, 0, 1, loc, relative=True)

            #attach metaData
            cmds.addAttr(loc, longName='metaParent', attributeType='message')

            cmds.connectAttr('%s.message' % nodes[2], '%s.metaParent' % loc)

            cmds.setAttr('%s.createJoints' % nodes[2], 'true', type='string')

        #one item selected
        if selCount == 2:
            #getting selection
            sel1 = cmds.ls(sl=True)[0]

            sel2 = cmds.ls(sl=True)[1]

            #create sphere
            nodes = self.sphereDist()

            #setup sphere
            cmds.pointConstraint(sel1, nodes[0])

            cmds.pointConstraint(sel2, nodes[1])

            #setup metaData
            cmds.setAttr('%s.createJoints' % nodes[2], 'false', type='string')

    def delete_pushButton_released(self):

        cmds.undoInfo(openChunk=True)

        for node in (cmds.ls(type='network')):
            if (cmds.attributeQuery('type', n=node, ex=True)) == True and \
            (cmds.getAttr('%s.type' % node)) == 'spherePreview':
                if (cmds.getAttr('%s.createJoints' % node)) == 'true':
                    #create joints
                    cmds.select(cl=True)
                    jnt1 = cmds.joint()

                    cmds.select(cl=True)
                    jnt2 = cmds.joint()

                    #setup joints
                    sph = cmds.listConnections('%s.sphere' % node,
                                               type='transform')
                    cmds.delete(cmds.pointConstraint(sph, jnt1))

                    grp = cmds.listConnections('%s.group' % node,
                                               type='transform')
                    cmds.delete(cmds.pointConstraint(grp, jnt2))

                    cmds.delete(cmds.aimConstraint(grp, jnt1))
                    cmds.makeIdentity(jnt1, apply=True)

                    cmds.delete(cmds.orientConstraint(jnt1, jnt2))
                    cmds.makeIdentity(jnt2, apply=True)

                    cmds.parent(jnt2, jnt1)

                for child in cmds.listConnections('%s.message' % node,
                                                  type='transform'):
                    cmds.delete(child)

        cmds.undoInfo(closeChunk=True)

    def help_pushButton_released(self):
        directory = os.path.dirname(__file__)
        readme = os.path.join(directory, 'README.md')
        f = open(readme, 'r')
        msg = f.read()
        f.close()
        cmds.confirmDialog(title='Help', message=msg, button=['OK'])


def show():
    win = Window()
    win.show()
