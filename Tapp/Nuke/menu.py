import nuke

#creating the Glapp menu
menubar = nuke.menu("Nuke")
m = menubar.addMenu("Tapp")

#adding gizmos menu
import utils.gizmos

#adding repository menu
nuke.menu('Nuke').addCommand('Tapp/Repository Change','import Tapp.Nuke.utils.repository as nur;nur.Change()' )