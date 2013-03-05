'''
CREDIT

http://marc.dubrois.free.fr

'''
#  User Menu for Maya
import xml.dom.minidom, os
import maya.mel as mel
import maya.cmds as cmds

def loadMenu():
    #    get user menu from menu.xml
    menuXml_path    = 'C:/Users/tokejepsen/Documents/GitHub/Tapp/Tapp/Maya/menu/menu.xml'
    
    #    get gMainWindow from mel command
    gMainWindow = mel.eval('$tmpVar=$gMainWindow')
    
    if os.path.exists(menuXml_path) :        
        menuLabel   = ''
        menuName    = 'userMenu'
        print ('Build Menu : ' + menuName)

        #    open xml document
        xmldoc                = xml.dom.minidom.parse(menuXml_path)
        
        #    search menu node
        for item in xmldoc.getElementsByTagName('menu'):
            
            val         = item.attributes["name"].value
            menuLabel   = val.encode('latin-1', 'replace')

            #    search and delete old menuName
            menuList    = cmds.window(gMainWindow, query=True, menuArray=True)
            
            for menu in menuList:
                if cmds.menu(menu, query=True, label=True) == menuLabel:
                    cmds.menu(menu, edit=True, deleteAllItems=True)
                    cmds.deleteUI(menu)
                    break
            
            #    Add userMenu to Maya Menu
            cmds.menu(menuName, parent=gMainWindow, tearOff=True, label=menuLabel, allowOptionBoxes=True)
            
            #    build each menu
            for child in item.childNodes:
                    if child.nodeType == 1 :
                        #loadMenu_recursive(child)                     
                        nodename    = child.nodeName
                        nodetype    = child.attributes["type"].value
                        
                        loadMenu_recursive(child, menuName)
                        

def loadMenu_recursive(xmlDoc, menuName):
    if xmlDoc.nodeType == 1 :
        nodename    = xmlDoc.nodeName
        nodetype    = xmlDoc.attributes["type"].value
        
        if nodetype == 'subMenu' :
            name        = xmlDoc.attributes["name"].value
            cmds.menuItem(parent=menuName, subMenu=True, tearOff=True, label=name)       
        
            for child in xmlDoc.childNodes:
                loadMenu_recursive(child, menuName)
                
            cmds.setParent( '..' )
            
        if nodetype == 'command' :
            name        = xmlDoc.attributes["name"].value
            comment     = xmlDoc.attributes["comment"].value
            commandExe  = xmlDoc.attributes["cmd"].value
            mode        = xmlDoc.attributes["mode"].value
            
            cmd  =commandExe.encode('latin-1', 'replace')
            if mode == 'mel':
                commandExe  = ('maya.mel.eval(\'' +  cmd + '\')')
                cmds.menuItem(label=name, command=commandExe, annotation=comment)
                
            if mode == 'python':
                cmds.menuItem(label=name, command=commandExe, annotation=comment)
                            
        if nodetype == 'separator' :
            cmds.menuItem( divider=True)