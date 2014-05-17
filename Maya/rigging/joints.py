from operator import itemgetter
from math import sqrt, pow

import pymel.core as pm
import maya.cmds as cmds

from Tapp.Maya.rigging import utils
reload(utils)


def PlaceOnComponent():
    # Variables to store selected edges,
    #verts and faces those edges are connected to
    verts = []
    edges = []
    faces = []
    shp = ''

    # Get the selection and flatten it.
    #Otherwise Maya might return lists and not individual elements
    sel = pm.selected(flatten=True)

    # Get the selected edges
    for s in sel:
        # Get the selections type
        objType = s.__class__.__name__

        shp = pm.PyNode(s.split('.')[0])

        # If the type is MeshEdge then append the edge to our list
        if objType == "MeshEdge":
            edges.append(s)

        if objType == "MeshFace":
            faces.append(s)

        if objType == "MeshVertex":
            verts.append(s)

    if verts:
        for vert in verts:
            jnts = createEdgeJoints(vert.connectedEdges())

            pm.select(clear=True)
            jnt = pm.joint()
            pm.xform(jnt, worldSpace=True,
                     translation=vert.getPosition(space='world'))
            pm.delete(pm.orientConstraint(jnts[0], jnts[1],
                                          jnts[2], jnts[3],
                                          jnt))
            pm.delete(jnts)
            pm.makeIdentity(jnt, r=True, apply=True)

    if faces:
        for face in faces:
            faceVerts = face.getVertices()
            faceVertsPos = [shp.vtx[faceVerts[0]].getPosition(space='world'),
                     shp.vtx[faceVerts[1]].getPosition(space='world'),
                     shp.vtx[faceVerts[2]].getPosition(space='world'),
                     shp.vtx[faceVerts[3]].getPosition(space='world')]

            avg = [float(sum(col)) / len(col) for col in zip(*faceVertsPos)]
            ySorted = sorted(faceVertsPos, key=itemgetter(1))
            highestVerts = [shp.vtx[faceVerts[faceVertsPos.index(ySorted[2])]],
                            shp.vtx[faceVerts[faceVertsPos.index(ySorted[3])]]]
            clusTfm = pm.cluster(highestVerts)[1]
            upLoc = pm.spaceLocator()
            pm.pointConstraint(clusTfm, upLoc)

            faceEdges = face.getEdges()
            faceEdges = [shp.e[faceEdges[0]],
                     shp.e[faceEdges[1]],
                     shp.e[faceEdges[2]],
                     shp.e[faceEdges[3]]]

            jnts = createEdgeJoints(faceEdges)

            pm.select(clear=True)
            jnt = pm.joint()
            pm.xform(jnt, worldSpace=True, translation=avg)
            pm.delete(pm.orientConstraint(jnts[0], jnts[1],
                                          jnts[2], jnts[3],
                                          jnt))
            pm.delete(jnts)

            pm.select(clear=True)
            aimLoc = pm.spaceLocator()
            pm.xform(aimLoc, worldSpace=True, translation=avg)
            pm.delete(pm.orientConstraint(jnt, aimLoc))
            pm.parent(aimLoc, jnt)
            aimLoc.tx.set(1)
            pm.parent(aimLoc, w=True)

            pm.delete(pm.aimConstraint(aimLoc, jnt, worldUpType='object',
                                       worldUpObject=upLoc))

            pm.delete(upLoc, aimLoc, clusTfm)
            pm.makeIdentity(jnt, r=True, apply=True)

    # Continue only if we have edges selected
    if edges:

        createEdgeJoints(edges)


def createEdgeJoints(edges):
    joints = []
    # Do this for every edge
    for edge in edges:
        # Get the vertices the edge is connected to
        edgeVerts = edge.connectedVertices()

        # Cluster the verts.
        #We will use this to get the position for our joint
        clusTfm = pm.cluster(edgeVerts)[1]

        pm.select(clear=True)
        # Create our joint
        jnt = pm.joint()

        # getPosition doesn't give us the correct result. This does
        pos = clusTfm.rotatePivot.get()
        # We don't need the cluster any more
        pm.delete(clusTfm)

        # Now we calculate the average normal
        normals = []
        for face in edge.connectedFaces():
            # Collect the normal of every face
            normals.append(face.getNormal(space="world"))

        # Variable that will store the sum of all normals
        normalsSum = pm.datatypes.Vector()
        for normal in normals:
            normalsSum += normal

        # This will be our vector for the x axis
        # Average normal.
        #We divide the normal by the total number of vectors
        xVec = (normalsSum / len(normals))

        # The vertex that has the highest position,
        #will be the vertex that our Y axis will point to
        for i, vert in enumerate(edgeVerts):
            # We take the first vert as our up vector
            if i == 0:
                upVec = edgeVerts[0].getPosition(space="world")

            # And compare the other to it
            vertPos = edgeVerts[i].getPosition(space="world")
            if vertPos[1] >= upVec[1]:
                upVec = vertPos

        # This gives us a vector that points from the center
        #of the selection to the highest vertex
        upVec = upVec - pos

        # We get the z vector from the cross product of our x vector
        #and the up vector
        zVec = xVec.cross(upVec)
        # Calculate the y vec the same way. We could use the upVec
        #but this way we make sure they are all correct
        yVec = zVec.cross(xVec)

        # Normalize all vectors so scaling doesn't get messed up
        xVec.normalize()
        yVec.normalize()
        zVec.normalize()

        # Construct the matrix from the vectors we calculated
        jntMtx = pm.dt.Matrix(xVec, yVec, zVec, pos)
        # And set the joints matrix to our new matrix
        jnt.setMatrix(jntMtx)

        # This transfers the rotation values
        #to the joint orientation values.
        pm.makeIdentity(jnt, r=True, apply=True)
        joints.append(jnt)
    return joints


def ParentToJoint():
    nodes = cmds.ls(selection=True)
    jnts = cmds.ls(selection=True, type='joint')
    nodes = list(set(nodes) - set(jnts))
    for node in nodes:
        distances = []
        for jnt in jnts:
            grp = cmds.group(empty=True)
            cmds.pointConstraint(node, grp)
            At = cmds.xform(grp, ws=True, q=True, t=True)
            Ax = At[0]
            Ay = At[1]
            Az = At[2]
            cmds.delete(grp)

            grp = cmds.group(empty=True)
            cmds.pointConstraint(jnt, grp)
            Bt = cmds.xform(grp, ws=True, q=True, t=True)
            Bx = Bt[0]
            By = Bt[1]
            Bz = Bt[2]
            cmds.delete(grp)

            distances.append(sqrt(pow(Ax - Bx, 2) + pow(Ay - By, 2) + pow(Az - Bz, 2)))

        minDist = min(distances)
        closestJnt = jnts[distances.index(minDist)]
        cmds.parentConstraint(closestJnt, node, maintainOffset=True)

ParentToJoint()

