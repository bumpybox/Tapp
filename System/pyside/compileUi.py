import os
import imp

import pysideuic


def compileUi(uiPath):

    uiFile = open(uiPath, 'r')

    parentdir = os.path.abspath(os.path.join(uiPath, os.pardir))
    filename = os.path.basename(os.path.splitext(uiPath)[0])

    pyFile = open(os.path.join(parentdir, filename) + '.py', 'w')

    pysideuic.compileUi(uiFile, pyFile)

    uiFile.close()
    pyFile.close()

    mod = imp.load_source(filename, os.path.join(parentdir, filename) + '.py')

    return mod
