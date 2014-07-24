import pymel.core as pm


def SeparateDeform(nodes, attributes, values):

    #setting keyframes
    for node in nodes:
        for attr in attributes:
            for value in values:
                currentTime = pm.currentTime()

                pm.currentTime(currentTime + 10.0, update=True)

                pm.setKeyframe(node, attribute=attr, value=value)

                for zeroAttr in attributes:
                    if attr != zeroAttr:
                        pm.setKeyframe(node, attribute=zeroAttr, value=0)

                if attr == attributes[0]:
                    pm.setKeyframe(node, attribute=attr, value=0,
                                   time=currentTime - 10.0)

                if attr == attributes[-1]:
                    pm.setKeyframe(node, attribute=attr, value=0,
                                   time=currentTime + 20.0)


def CombineDeform(nodes, attributes, values):

    #setting keyframes
    for attr in attributes:
        for value in values:
            currentTime = pm.currentTime()

            pm.currentTime(currentTime + 10.0, update=True)

            pm.setKeyframe(nodes, attribute=attr, value=value)

            for zeroAttr in attributes:
                if attr != zeroAttr:
                    pm.setKeyframe(nodes, attribute=zeroAttr, value=0)

            if attr == attributes[0]:
                pm.setKeyframe(nodes, attribute=attr, value=0,
                               time=currentTime - 10.0)

            if attr == attributes[-1]:
                pm.setKeyframe(nodes, attribute=attr, value=0,
                               time=currentTime + 20.0)


sel = pm.ls(selection=True)
attributes = ['rx', 'ry', 'rz']
values = [90, -90]

SeparateDeform(sel, attributes, values)
