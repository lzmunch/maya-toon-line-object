# renderSubdivisions.py >>>>>

import maya.cmds as cmds

selectionList = cmds.ls(orderedSelection=True)

for objName in selectionList:
    cmds.setAttr(objName + ".aiSubdivType", 1);
    cmds.setAttr(objName + ".aiSubdivIterations", 2);
    print("set render subdivisions foir "  + objName)


# <<<<< end script