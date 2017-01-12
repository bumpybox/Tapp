import pymel.core as pm


def SeparateDeform(nodes, attributes, values, interval=10.0):

    #setting keyframes
    for node in nodes:
        for attr in attributes:
            for value in values:
                currentTime = pm.currentTime()

                pm.currentTime(currentTime + interval, update=True)

                pm.setKeyframe(node, attribute=attr, value=value)

                for zeroAttr in attributes:
                    if attr != zeroAttr:
                        pm.setKeyframe(node, attribute=zeroAttr, value=0)

                if attr == attributes[0]:
                    pm.setKeyframe(node, attribute=attr, value=0,
                                   time=currentTime - interval)

                if attr == attributes[-1]:
                    pm.setKeyframe(node, attribute=attr, value=0,
                                   time=currentTime + (interval * 2))


def CombineDeform(nodes, attributes, values, interval=10.0):

    #setting keyframes
    for attr in attributes:
        for value in values:
            currentTime = pm.currentTime()

            pm.currentTime(currentTime + interval, update=True)

            pm.setKeyframe(nodes, attribute=attr, value=(value/len(nodes)))

            for zeroAttr in attributes:
                if attr != zeroAttr:
                    pm.setKeyframe(nodes, attribute=zeroAttr, value=0)

            if attr == attributes[0]:
                pm.setKeyframe(nodes, attribute=attr, value=0,
                               time=currentTime - interval)

            if attr == attributes[-1]:
                pm.setKeyframe(nodes, attribute=attr, value=0,
                               time=currentTime + (interval * 2))


sel = pm.ls(selection=True)
attributes = ['rx', 'ry', 'rz']
values = [90, -90]

SeparateDeform(sel, attributes, values, 20.0)
#CombineDeform(sel, attributes, values, 20.0)
