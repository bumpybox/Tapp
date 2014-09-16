import json
import pymel.core as pm
from _ast import Delete


def Export(data):
    multipleFilters = "JSON Files (*.json)"
    f = pm.fileDialog2(fileMode=0, fileFilter=multipleFilters)
    if f:
        f = open(f[0], 'w')
        json.dump(data, f)
        f.close()


def Import():
    multipleFilters = "JSON Files (*.json)"
    f = pm.fileDialog2(fileMode=1, fileFilter=multipleFilters)
    if f:
        if isinstance(f, list):
            f = f[0]
        f = open(f, 'r')
        return json.load(f)
    else:
        return None


def DeleteConnections(node):

    for conn in node.listConnections(plugs=True, connections=True):
        try:
            pm.disconnectAttr(conn[0])
        except:
            pass


def GetConnections(node):
    source = []
    for conn in node.listConnections(d=False, s=True, plugs=True,
                                     connections=True):
        exportConn = []
        exportConn.append(conn[0].name())
        exportConn.append(conn[1].name())
        source.append(exportConn)
    destination = []
    for conn in node.listConnections(d=True, s=False, plugs=True,
                                     connections=True):
        exportConn = []
        exportConn.append(conn[0].name())
        exportConn.append(conn[1].name())
        destination.append(exportConn)

    return [source, destination]


def SetConnections(data):
    source = data[0]
    destination = data[1]

    for conn in source:
        attr1 = pm.PyNode(conn[0])
        attr2 = pm.PyNode(conn[1])
        pm.connectAttr(attr2, attr1, force=True)

    for conn in destination:
        attr1 = pm.PyNode(conn[0])
        attr2 = pm.PyNode(conn[1])
        pm.connectAttr(attr1, attr2, force=True)

#ExportData(data)
data = [[[u'left_wrist_driver.translateX', u'left_wrist_driver_parentConstraint1.constraintTranslateX'], [u'left_wrist_driver.translateY', u'left_wrist_driver_parentConstraint1.constraintTranslateY'], [u'left_wrist_driver.translateZ', u'left_wrist_driver_parentConstraint1.constraintTranslateZ'], [u'left_wrist_driver.rotateX', u'left_wrist_driver_parentConstraint1.constraintRotateX'], [u'left_wrist_driver.rotateY', u'left_wrist_driver_parentConstraint1.constraintRotateY'], [u'left_wrist_driver.rotateZ', u'left_wrist_driver_parentConstraint1.constraintRotateZ']], [[u'left_wrist_driver.translate', u'left_thumb_in_null_parentConstraint1.target[0].targetTranslate'], [u'left_wrist_driver.translate', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetTranslate'], [u'left_wrist_driver.translate', u'left_indexfinger_in_null_parentConstraint1.target[0].targetTranslate'], [u'left_wrist_driver.translate', u'left_littlefinger_in_null_parentConstraint1.target[0].targetTranslate'], [u'left_wrist_driver.translate', u'left_wrist_bind_parentConstraint1.target[0].targetTranslate'], [u'left_wrist_driver.rotate', u'left_thumb_in_null_parentConstraint1.target[0].targetRotate'], [u'left_wrist_driver.rotate', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetRotate'], [u'left_wrist_driver.rotate', u'left_indexfinger_in_null_parentConstraint1.target[0].targetRotate'], [u'left_wrist_driver.rotate', u'left_littlefinger_in_null_parentConstraint1.target[0].targetRotate'], [u'left_wrist_driver.rotate', u'left_wrist_bind_parentConstraint1.target[0].targetRotate'], [u'left_wrist_driver.scale', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetScale'], [u'left_wrist_driver.scale', u'left_thumb_in_null_parentConstraint1.target[0].targetScale'], [u'left_wrist_driver.scale', u'left_indexfinger_in_null_parentConstraint1.target[0].targetScale'], [u'left_wrist_driver.scale', u'left_littlefinger_in_null_parentConstraint1.target[0].targetScale'], [u'left_wrist_driver.scale', u'left_indexfinger_in_driver.inverseScale'], [u'left_wrist_driver.scale', u'left_littlefinger_in_driver.inverseScale'], [u'left_wrist_driver.scale', u'left_thumb_in_driver.inverseScale'], [u'left_wrist_driver.scale', u'left_wrist_bind_parentConstraint1.target[0].targetScale'], [u'left_wrist_driver.rotateOrder', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetRotateOrder'], [u'left_wrist_driver.rotateOrder', u'left_thumb_in_null_parentConstraint1.target[0].targetRotateOrder'], [u'left_wrist_driver.rotateOrder', u'left_indexfinger_in_null_parentConstraint1.target[0].targetRotateOrder'], [u'left_wrist_driver.rotateOrder', u'left_littlefinger_in_null_parentConstraint1.target[0].targetRotateOrder'], [u'left_wrist_driver.rotateOrder', u'left_wrist_bind_parentConstraint1.target[0].targetRotateOrder'], [u'left_wrist_driver.rotateOrder', u'left_wrist_driver_parentConstraint1.constraintRotateOrder'], [u'left_wrist_driver.parentInverseMatrix[0]', u'left_wrist_driver_parentConstraint1.constraintParentInverseMatrix'], [u'left_wrist_driver.rotatePivot', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetRotatePivot'], [u'left_wrist_driver.rotatePivot', u'left_thumb_in_null_parentConstraint1.target[0].targetRotatePivot'], [u'left_wrist_driver.rotatePivot', u'left_indexfinger_in_null_parentConstraint1.target[0].targetRotatePivot'], [u'left_wrist_driver.rotatePivot', u'left_littlefinger_in_null_parentConstraint1.target[0].targetRotatePivot'], [u'left_wrist_driver.rotatePivot', u'left_wrist_bind_parentConstraint1.target[0].targetRotatePivot'], [u'left_wrist_driver.rotatePivot', u'left_wrist_driver_parentConstraint1.constraintRotatePivot'], [u'left_wrist_driver.rotatePivotTranslate', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetRotateTranslate'], [u'left_wrist_driver.rotatePivotTranslate', u'left_thumb_in_null_parentConstraint1.target[0].targetRotateTranslate'], [u'left_wrist_driver.rotatePivotTranslate', u'left_indexfinger_in_null_parentConstraint1.target[0].targetRotateTranslate'], [u'left_wrist_driver.rotatePivotTranslate', u'left_littlefinger_in_null_parentConstraint1.target[0].targetRotateTranslate'], [u'left_wrist_driver.rotatePivotTranslate', u'left_wrist_bind_parentConstraint1.target[0].targetRotateTranslate'], [u'left_wrist_driver.rotatePivotTranslate', u'left_wrist_driver_parentConstraint1.constraintRotateTranslate'], [u'left_wrist_driver.jointOrient', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetJointOrient'], [u'left_wrist_driver.jointOrient', u'left_thumb_in_null_parentConstraint1.target[0].targetJointOrient'], [u'left_wrist_driver.jointOrient', u'left_indexfinger_in_null_parentConstraint1.target[0].targetJointOrient'], [u'left_wrist_driver.jointOrient', u'left_littlefinger_in_null_parentConstraint1.target[0].targetJointOrient'], [u'left_wrist_driver.jointOrient', u'left_wrist_bind_parentConstraint1.target[0].targetJointOrient'], [u'left_wrist_driver.jointOrient', u'left_wrist_driver_parentConstraint1.constraintJointOrient'], [u'left_wrist_driver.parentMatrix[0]', u'left_thumb_in_null_parentConstraint1.target[0].targetParentMatrix'], [u'left_wrist_driver.parentMatrix[0]', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetParentMatrix'], [u'left_wrist_driver.parentMatrix[0]', u'left_indexfinger_in_null_parentConstraint1.target[0].targetParentMatrix'], [u'left_wrist_driver.parentMatrix[0]', u'left_littlefinger_in_null_parentConstraint1.target[0].targetParentMatrix'], [u'left_wrist_driver.parentMatrix[0]', u'left_wrist_bind_parentConstraint1.target[0].targetParentMatrix'], [u'left_wrist_driver.segmentScaleCompensate', u'left_thumb_in_null_parentConstraint1.target[0].targetScaleCompensate'], [u'left_wrist_driver.segmentScaleCompensate', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetScaleCompensate'], [u'left_wrist_driver.segmentScaleCompensate', u'left_indexfinger_in_null_parentConstraint1.target[0].targetScaleCompensate'], [u'left_wrist_driver.segmentScaleCompensate', u'left_littlefinger_in_null_parentConstraint1.target[0].targetScaleCompensate'], [u'left_wrist_driver.segmentScaleCompensate', u'left_wrist_bind_parentConstraint1.target[0].targetScaleCompensate'], [u'left_wrist_driver.inverseScale', u'left_thumb_in_null_parentConstraint1.target[0].targetInverseScale'], [u'left_wrist_driver.inverseScale', u'left_arm_switch_ctrl_parentConstraint1.target[0].targetInverseScale'], [u'left_wrist_driver.inverseScale', u'left_indexfinger_in_null_parentConstraint1.target[0].targetInverseScale'], [u'left_wrist_driver.inverseScale', u'left_littlefinger_in_null_parentConstraint1.target[0].targetInverseScale'], [u'left_wrist_driver.inverseScale', u'left_wrist_bind_parentConstraint1.target[0].targetInverseScale']]]
#sel = pm.ls(selection=True)[0]
#data = GetConnections(sel)
#Export(data)
#DeleteConnections(sel)
data = Import()
SetConnections(data)
