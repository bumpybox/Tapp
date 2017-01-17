import utils


def setup():

    if utils.get_host().startswith("maya"):
        add_filemenu_maya()

    if utils.get_host().startswith("nuke"):
        add_filemenu_nuke()

    print("tapp: Loaded successfully.")


def add_filemenu_nuke():

    import nuke

    menubar = nuke.menu("Nuke")
    menu = menubar.addMenu("Tapp")

    cmd = "import tapp;reload(tapp)"
    cmd += ";win = tapp.show()"
    menu.addCommand("Launch", cmd)


def add_filemenu_maya():

    import maya.cmds as cmds

    cmds.evalDeferred("tapp.utils.lib._add_filemenu_maya()")


def _add_filemenu_maya():

    import maya.cmds as cmds
    import maya.mel as mel

    gMainWindow = mel.eval("$tmpVar=$gMainWindow")

    menuList = cmds.window(gMainWindow, query=True, menuArray=True)
    if "tapp" in menuList:
        cmds.deleteUI("tapp")

    menu = cmds.menu("tapp", label="Tapp",
                     parent=gMainWindow)

    cmd = "import tapp;reload(tapp)"
    cmd += ";win = tapp.show()"
    cmds.menuItem(label="Launch", parent=menu, command=cmd)
