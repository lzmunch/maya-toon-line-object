# toonLineEditor.py >>>>>

import maya.cmds as cmds
import maya.mel as mm 
import sortTool
import os

# original mel script is broken, use this instead
# use directory of current scene file to find scripts path
sceneDir = os.path.dirname(cmds.file(query=True, sceneName=True)) 
scriptsPath = sceneDir.replace(os.path.sep, '/') + '/scripts'
mm.eval('source "' + scriptsPath + '/toonLineEditorScript/doPaintEffectsToGeom_Custom.mel"')

# global vars and config
toonParentGrp = 'pfxToon'
toonLinesGrp = 'pfxToonLines'
toonMeshesGrp = 'pfxToonMeshes'
cutPlanesGrp = 'cutPlanes'

lineBaseName = 'pfxToon'
meshBaseName = 'pfxToonMesh'
defaultWidth = 3
defaultThinning = defaultWidth * 10

toonLinePreset = {
    'creaseLines': 0,
    'intersectionLines': 1,
    'profileLines': 0,
    'borderLines': 0,
    'resampleIntersection': 1,
    'lineWidth': 1,
    'lineEndThinning': 10
}

class toonLinesWindow(object):
    # constructor
    def __init__(self):

        # window settings
        self.window = 'ToonLinesWin'
        self.tilte = 'Toon Lines Custom Editor'
        self.size = (300, 800)
        
        # delete if window already open
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)
            
        # create new window
        self.window = cmds.window(self.window, title=self.tilte, widthHeight=self.size)
        
        cmds.columnLayout(columnAttach=('both', 5), adjustableColumn=True, rowSpacing=5)
        
        # Toon line helpers
        cmds.separator(height=10)
        cmds.text(label='Toon Line', font='boldLabelFont')
        cmds.separator(height=10)

        cmds.text(label='1. Create groups for toon lines and meshes')
        self.setupOutlinerBtn = cmds.button(label='Setup Outliner', c=self.setupOutliner, width=100)

        cmds.separator(height=3, style='none')
        cmds.text(label='2. Select 2 objects and create toon line')        
        self.createToonBtn = cmds.button(label='Create pfxToon', c=self.createPfxToon, width=100)

        cmds.separator(height=3, style='none')
        cmds.text(label='3. Select toon line and adjust settings')
        self.lineWidth = cmds.floatFieldGrp(label='Width', value1=defaultWidth, cc=self.applySettings, precision=2)
        self.lineEndThinning = cmds.floatFieldGrp(label='End Thinning', value1=defaultThinning, cc=self.applySettings, precision=2)
        self.applyBtn = cmds.button(label='Apply Settings', c=self.applySettings, width=100)
        
        cmds.separator(height=3, style='none')
        cmds.text(label='4. Select toon line and convert to mesh')
        self.toPolyBtn = cmds.button(label='Render to Poly', c=self.renderToPoly, width=100)
        
        cmds.separator(height=3, style='none')
        cmds.text(label='Other Toon Utils')
        self.sortBtn = cmds.button(label='Sort Outliner', c=self.sortOutliner, width=100)
        
        cmds.separator(height=10, style='none')
        
        # Render helpers
        cmds.separator(height=10)
        cmds.text(label='Rendering', font='boldLabelFont')
        cmds.separator(height=10)

        cmds.text(label='Turn on "Render Subdivisions" option \n for all selected objects')
        self.numRenderSubdivs = cmds.floatFieldGrp(label='Subdivisions', value1=defaultWidth, cc=self.applySettings, precision=0)
        self.renderSubdivBtn = cmds.button(label='Turn On Render Subdivisions', c=self.renderSubdivisions)
        
        # display
        cmds.showWindow()
        
    # create toonLines and toonMeshes group in outliner
    def setupOutliner(self, *args):
       cmds.group( em=True, name=toonParentGrp )
       
       cmds.group( em=True, name=toonLinesGrp )
       cmds.parent(toonLinesGrp, toonParentGrp)

       cmds.group( em=True, name=toonMeshesGrp )
       cmds.parent(toonMeshesGrp, toonParentGrp)
       
       cmds.group( em=True, name=cutPlanesGrp )
       cmds.parent(cutPlanesGrp, toonParentGrp)
       
       # init cut plane, turn off visibility in render
       cutPlaneName = cmds.polyPlane(sx=1, sy=1)
       cmds.select(cutPlaneName)
       cmds.rename('cutPlane00')
       cmds.parent('cutPlane00', cutPlanesGrp)
       
       disableList = ['primaryVisibility', 'castsShadows', 'aiVisibleInVolume', 'aiSelfShadows']
       for attr in disableList:
           cmds.setAttr('cutPlaneShape0.' + attr, 0)
        
        
    # create toon outline from two selected objects
    # rename by scanning toonLinesGrp for next available number
    # make child of toonLinesGrp
    def createPfxToon(self, *args):
        # check if two objects are selected
        if len(cmds.ls(selection=True)) < 2:
            cmds.confirmDialog(m="Need to select two objects", b="Okay")
            return

        # assign toon outline
        mm.eval('''
            assignNewPfxToon();
            $selected = `ls -selection`;
            string $pfxToonShape2 = $selected[0];
        ''');
        # applyPresetToNode $selected[0] "" "" "artDirectableLine" 1;
        
        newToon = cmds.ls(orderedSelection=True)[0]
        
        # setup base attributes (instead of preset)
        for attr, val in toonLinePreset.items():
            cmds.setAttr(newToon + '.' + attr, val)
        
        # rename and reparent
        newToonName = lineBaseName + self.getNewID();
        newToonParent = cmds.listRelatives(newToon, parent=True)
        cmds.select(newToonParent, r=True)
        cmds.rename(newToonName)
        cmds.parent(newToonName, toonLinesGrp)
        
    # apply toon line settings
    def applySettings(self, *args):
        
        selectionList = cmds.ls(orderedSelection=True)
        
        lineWidth = cmds.floatFieldGrp(self.lineWidth, query=True, value1=True)
        lineEndThinning = cmds.floatFieldGrp(self.lineEndThinning, query=True, value1=True)
        
        for pfxToon in selectionList:
            cmds.setAttr(pfxToon + '.lineWidth', lineWidth)
            cmds.setAttr(pfxToon + '.lineEndThinning', lineEndThinning)        
            
    # convert selected pfxToon objects to meshes
    # rename based on selected toon line
    # make child of toonMeshesGrp
    def renderToPoly(self, *args):
        selectionList = cmds.ls(orderedSelection=True)
        for pfxToon in selectionList:
            # check if mesh for this toon line has already been created
            if self.meshExists(pfxToon):
                cmds.confirmDialog(m="Skipping " + pfxToon + ". Mesh already exists", b="Okay")
                continue
            
            cmds.select(cl=True)
            cmds.select(pfxToon)
            
            mm.eval('doPaintEffectsToPoly( 1,0,1,0,100000);')
            
            #cmds.select(cl=True)
            shapeName = cmds.ls(orderedSelection=True)[0]
            transformName = cmds.listRelatives(shapeName, parent=True)
            parentName = cmds.listRelatives(transformName, parent=True)

            cmds.select(transformName, r=True)

            # put new toon mesh in toonMeshesGrp
            cmds.parent(transformName, toonMeshesGrp)
            cmds.delete(parentName);
            
            # rename ID
            cmds.rename(meshBaseName + pfxToon[-3:])     
            
            cmds.xform(centerPivots=True)
            
            print('rendered ' + pfxToon)            
            
    # set render subdivisions for selected objects
    # can't do this in batch normally
    def renderSubdivisions(self, *args):
        selectionList = cmds.ls(orderedSelection=True)
        for meshGroup in selectionList:
            cmds.select(cl=True)
            cmds.select(meshGroup)
            # setAttr "pasted__front_seats_pCube2Shape.aiSubdivType" 2;
            # cmds.setAttr(meshGroup + '|Main|MainShape.aiSubdivType', 1);
            # cmds.setAttr('|' + meshGroup + '|Main|MainShape.aiSubdivIterations', 4);
            
            try:
                numRenderSubdivs = cmds.floatFieldGrp(self.numRenderSubdivs, query=True, value1=True)
                cmds.setAttr(meshGroup + 'Shape.aiSubdivType', 1);
                cmds.setAttr(meshGroup + 'Shape.aiSubdivIterations', numRenderSubdivs);
            except:
                print('Error: skipping ' + meshGroup)
            
            cmds.select(cl=True)
            print('Update Render Subdivisions for ' + meshGroup)
            
    # scan toonLinesGrp for next available number
    def getNewID(self):
        existing = cmds.listRelatives( toonLinesGrp, children=True)
        print(existing)
        if existing:
            newID = len(existing)
        else:
            newID = 0
            
        # convert to 2 digit number string and make unique from automatically created names
        return '_' + str(newID).zfill(2)

    # check if a mesh has already been created for a given toon line
    def meshExists(self, pfxToon):
        mesh = meshBaseName + pfxToon[-3:]
        existing = cmds.listRelatives( toonMeshesGrp, children=True)
        if not existing:
            existing = []      
        if mesh in existing:
            return True
        else:
            return False
       
    # sort hierarchy, make it easier to find stuff     
    def sortOutliner(self, *args):
        # save current selection
        selectionList = cmds.ls(orderedSelection=True)

        cmds.select([toonLinesGrp, toonMeshesGrp])
        sortTool.sort_selected_children()
        
        # restore old selection
        cmds.select(selectionList, r=True);
       

toonLinesWindow()
    
# <<<<< end script# testToonLine.py >>>>>

import maya.cmds as cmds
import maya.mel as mm 
import sortTool

# original mel script is broken, use this instead
scriptsPath = 'C:/Users/etc-student/Documents/maya/2022/scripts'
mm.eval('source "' + scriptsPath + '/doPaintEffectsToGeom_Custom.mel"')

# global vars and config
toonParentGrp = 'pfxToon'
toonLinesGrp = 'pfxToonLines'
toonMeshesGrp = 'pfxToonMeshes'
cutPlanesGrp = 'cutPlanes'

lineBaseName = 'pfxToon'
meshBaseName = 'pfxToonMesh'
defaultWidth = 3
defaultThinning = defaultWidth * 10

toonLinePreset = {
    'creaseLines': 0,
    'intersectionLines': 1,
    'profileLines': 0,
    'borderLines': 0,
    'resampleIntersection': 1,
    'lineWidth': 1,
    'lineEndThinning': 10
}

class toonLinesWindow(object):
    # constructor
    def __init__(self):

        # window settings
        self.window = 'ToonLinesWin'
        self.tilte = 'Toon Lines Custom Editor'
        self.size = (300, 800)
        
        # delete if window already open
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)
            
        # create new window
        self.window = cmds.window(self.window, title=self.tilte, widthHeight=self.size)
        
        cmds.columnLayout(columnAttach=('both', 5), adjustableColumn=True, rowSpacing=5)
        
        # Toon line helpers
        cmds.separator(height=10)
        cmds.text(label='Toon Line', font='boldLabelFont')
        cmds.separator(height=10)

        cmds.text(label='1. Create groups for toon lines and meshes')
        self.setupOutlinerBtn = cmds.button(label='Setup Outliner', c=self.setupOutliner, width=100)

        cmds.separator(height=3, style='none')
        cmds.text(label='2. Select 2 objects and create toon line')        
        self.createToonBtn = cmds.button(label='Create pfxToon', c=self.createPfxToon, width=100)

        cmds.separator(height=3, style='none')
        cmds.text(label='3. Select toon line and adjust settings')
        self.lineWidth = cmds.floatFieldGrp(label='Width', value1=defaultWidth, cc=self.applySettings, precision=2)
        self.lineEndThinning = cmds.floatFieldGrp(label='End Thinning', value1=defaultThinning, cc=self.applySettings, precision=2)
        self.applyBtn = cmds.button(label='Apply Settings', c=self.applySettings, width=100)
        
        cmds.separator(height=3, style='none')
        cmds.text(label='4. Select toon line and convert to mesh')
        self.toPolyBtn = cmds.button(label='Render to Poly', c=self.renderToPoly, width=100)
        
        cmds.separator(height=3, style='none')
        cmds.text(label='Other Toon Utils')
        self.sortBtn = cmds.button(label='Sort Outliner', c=self.sortOutliner, width=100)
        
        cmds.separator(height=10, style='none')
        
        # Render helpers
        cmds.separator(height=10)
        cmds.text(label='Rendering', font='boldLabelFont')
        cmds.separator(height=10)

        cmds.text(label='Turn on "Render Subdivisions" option \n for all selected objects')
        self.numRenderSubdivs = cmds.floatFieldGrp(label='Subdivisions', value1=defaultWidth, cc=self.applySettings, precision=0)
        self.renderSubdivBtn = cmds.button(label='Turn On Render Subdivisions', c=self.renderSubdivisions)
        
        # display
        cmds.showWindow()
        
    # create toonLines and toonMeshes group in outliner
    def setupOutliner(self, *args):
       cmds.group( em=True, name=toonParentGrp )
       
       cmds.group( em=True, name=toonLinesGrp )
       cmds.parent(toonLinesGrp, toonParentGrp)

       cmds.group( em=True, name=toonMeshesGrp )
       cmds.parent(toonMeshesGrp, toonParentGrp)
       
       cmds.group( em=True, name=cutPlanesGrp )
       cmds.parent(cutPlanesGrp, toonParentGrp)
       
       # init cut plane, turn off visibility in render
       cutPlaneName = cmds.polyPlane(sx=1, sy=1)
       cmds.select(cutPlaneName)
       cmds.rename('cutPlane00')
       cmds.parent('cutPlane00', cutPlanesGrp)
       
       disableList = ['primaryVisibility', 'castsShadows', 'aiVisibleInVolume', 'aiSelfShadows']
       for attr in disableList:
           cmds.setAttr('cutPlaneShape0.' + attr, 0)
        
        
    # create toon outline from two selected objects
    # rename by scanning toonLinesGrp for next available number
    # make child of toonLinesGrp
    def createPfxToon(self, *args):
        # check if two objects are selected
        if len(cmds.ls(selection=True)) < 2:
            cmds.confirmDialog(m="Need to select two objects", b="Okay")
            return

        # assign toon outline
        mm.eval('''
            assignNewPfxToon();
            $selected = `ls -selection`;
            string $pfxToonShape2 = $selected[0];
        ''');
        # applyPresetToNode $selected[0] "" "" "artDirectableLine" 1;
        
        newToon = cmds.ls(orderedSelection=True)[0]
        
        # setup base attributes (instead of preset)
        for attr, val in toonLinePreset.items():
            cmds.setAttr(newToon + '.' + attr, val)
        
        # rename and reparent
        newToonName = lineBaseName + self.getNewID();
        newToonParent = cmds.listRelatives(newToon, parent=True)
        cmds.select(newToonParent, r=True)
        cmds.rename(newToonName)
        cmds.parent(newToonName, toonLinesGrp)
        
    # apply toon line settings
    def applySettings(self, *args):
        
        selectionList = cmds.ls(orderedSelection=True)
        
        lineWidth = cmds.floatFieldGrp(self.lineWidth, query=True, value1=True)
        lineEndThinning = cmds.floatFieldGrp(self.lineEndThinning, query=True, value1=True)
        
        for pfxToon in selectionList:
            cmds.setAttr(pfxToon + '.lineWidth', lineWidth)
            cmds.setAttr(pfxToon + '.lineEndThinning', lineEndThinning)        
            
    # convert selected pfxToon objects to meshes
    # rename based on selected toon line
    # make child of toonMeshesGrp
    def renderToPoly(self, *args):
        selectionList = cmds.ls(orderedSelection=True)
        for pfxToon in selectionList:
            # check if mesh for this toon line has already been created
            if self.meshExists(pfxToon):
                cmds.confirmDialog(m="Skipping " + pfxToon + ". Mesh already exists", b="Okay")
                continue
            
            cmds.select(cl=True)
            cmds.select(pfxToon)
            
            mm.eval('doPaintEffectsToPoly( 1,0,1,0,100000);')
            
            #cmds.select(cl=True)
            shapeName = cmds.ls(orderedSelection=True)[0]
            transformName = cmds.listRelatives(shapeName, parent=True)
            parentName = cmds.listRelatives(transformName, parent=True)

            cmds.select(transformName, r=True)

            # put new toon mesh in toonMeshesGrp
            cmds.parent(transformName, toonMeshesGrp)
            cmds.delete(parentName);
            
            # rename ID
            cmds.rename(meshBaseName + pfxToon[-3:])     
            
            cmds.xform(centerPivots=True)
            
            print('rendered ' + pfxToon)            
            
    # set render subdivisions for selected objects
    # can't do this in batch normally
    def renderSubdivisions(self, *args):
        selectionList = cmds.ls(orderedSelection=True)
        for meshGroup in selectionList:
            cmds.select(cl=True)
            cmds.select(meshGroup)
            # setAttr "pasted__front_seats_pCube2Shape.aiSubdivType" 2;
            # cmds.setAttr(meshGroup + '|Main|MainShape.aiSubdivType', 1);
            # cmds.setAttr('|' + meshGroup + '|Main|MainShape.aiSubdivIterations', 4);
            
            try:
                numRenderSubdivs = cmds.floatFieldGrp(self.numRenderSubdivs, query=True, value1=True)
                cmds.setAttr(meshGroup + 'Shape.aiSubdivType', 1);
                cmds.setAttr(meshGroup + 'Shape.aiSubdivIterations', numRenderSubdivs);
            except:
                print('Error: skipping ' + meshGroup)
            
            cmds.select(cl=True)
            print('Update Render Subdivisions for ' + meshGroup)
            
    # scan toonLinesGrp for next available number
    def getNewID(self):
        existing = cmds.listRelatives( toonLinesGrp, children=True)
        print(existing)
        if existing:
            newID = len(existing)
        else:
            newID = 0
            
        # convert to 2 digit number string and make unique from automatically created names
        return '_' + str(newID).zfill(2)

    # check if a mesh has already been created for a given toon line
    def meshExists(self, pfxToon):
        mesh = meshBaseName + pfxToon[-3:]
        existing = cmds.listRelatives( toonMeshesGrp, children=True)
        if not existing:
            existing = []      
        if mesh in existing:
            return True
        else:
            return False
       
    # sort hierarchy, make it easier to find stuff     
    def sortOutliner(self, *args):
        # save current selection
        selectionList = cmds.ls(orderedSelection=True)

        cmds.select([toonLinesGrp, toonMeshesGrp])
        sortTool.sort_selected_children()
        
        # restore old selection
        cmds.select(selectionList, r=True);
       
toonLinesWindow()
    
# <<<<< end script