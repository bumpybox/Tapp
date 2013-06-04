'''
- MetaClassFinder
    - Graph Selected Networks
        - only opens node editor, and doesnt graph the nodes
- MetaRig
    - addMetaSubSystem
        - can only choose between ('Left','Right','Centre'), would be good to be able to choose anything or at least lower case of existing. Plus possibly ('top','bottom','front','back') for dealing with face and quadropeds
        - could '*_System' string ending be optional?
    - addRigCtrl
        - tried setting the CTRL_prefix to something else, and it didn't update when adding a control
        - was wondering how to use the 'addRigCtrl' and meta data on control?
            - basically im building a system that uses sockets, plugs and controls, and I would like to describe the node type in a meta data form rather than relying on attribute strings.

'''