import pymel.core as pm


def Snap(target, source, translation=True, rotation=True):
    ''' Snaps source object to target object.
    If point is True, translation will snap.
    If orient is True, orientation will snap.
    If source is None, then it looks for lists for translation,rotation and scale
    '''

    #if source doesnt exists and passing in transform lists
    if not source:
        if isinstance(translation, list):
            pm.xform(target, ws=True, translation=translation)
        if isinstance(rotation, list):
            pm.xform(target, ws=True, rotation=rotation)

        return

    #translation
    if translation:
        trans = pm.xform(source, q=True, ws=True, translation=True)
        pm.xform(target, ws=True, translation=trans)

    #orientation
    if rotation:
        rot = pm.xform(source, q=True, ws=True, rotation=True)
        pm.xform(target, ws=True, rotation=rot)


def getConnectedNodes(node, attribute):

    result = []

    for conn in node.listConnections(connections=True, type='transform'):
        if conn[0].split('.')[1] == attribute:
            result.append(conn[1])

    return result


def switch(space, timeRange=False, start=0, end=0):

    #undo enable
    pm.undoInfo(openChunk=True)

    sel = pm.ls(selection=True)

    for node in sel:
        cnt = getConnectedNodes(node, 'control')[0]

        controls = []
        for obj in getConnectedNodes(cnt, 'message'):

            #IK switch
            if space == 'IK':
                if obj.space.get() == space:
                    if timeRange:
                        for count in xrange(start, end):
                            pm.currentTime(count)
                            switch = getConnectedNodes(obj, 'switch')[0]
                            Snap(obj, switch)

                            cnt.blend.set(1)
                    else:
                        switch = getConnectedNodes(obj, 'switch')[0]
                        Snap(obj, switch)

                        cnt.blend.set(1)

            #FK control finding
            if space == 'FK':
                if obj.space.get() == space:
                    controls.append(obj)

        #FK switch
        controls.sort(key=lambda x: x.chain.get())
        if timeRange:
            for count in xrange(start, end):
                pm.currentTime(count)
                for obj in controls:
                    switch = getConnectedNodes(obj, 'switch')[0]
                    Snap(obj, switch)

                    cnt.blend.set(0)
        else:
            for obj in controls:
                switch = getConnectedNodes(obj, 'switch')[0]
                Snap(obj, switch)

                cnt.blend.set(0)

    pm.undoInfo(closeChunk=True)
