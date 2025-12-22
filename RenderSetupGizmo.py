import maya.cmds as cmds
import mtoa.aovs as aovs


movementDir = {'dolly': 'dollyCTRL', 'truck': 'truckCTRL', 'boom': 'boomCTRL',
                'pan': 'panCTRL', 'tilt':'tiltCTRL', 'roll':'rollCTRL'}


def makeArrow():
    length = 1
    arrowHead = cmds.curve(name = "arrow_CTRL",d=1, p=[(0,0,-1), (length,0,-1), (length,0,-2), (length+2,0,0), (length,0,2), (length,0,1), (0,0,1)])
    return(arrowHead)
    
        
def makeControl(controlName, x, y, z, rx, ry):
    lineFirst = makeArrow()
    cmds.scale(0.3,0.3,0.3)
    cmds.rotate(0,90,0)
    
    lineSecond = makeArrow()
    cmds.scale(0.3,0.3,0.3)
    cmds.rotate(0,270,0)
    
    lineControl = cmds.attachCurve(lineSecond,lineFirst, rpo = False, name = controlName)
    cmds.makeIdentity(apply=True, translate=1, rotate=1, scale=1, normal=0)
    cmds.delete(lineSecond, lineFirst)
    
    # Adjust control to correct position
    cmds.move(x, y, z)
    cmds.scale(1, 1, 1)
    cmds.rotate(rx, ry, 0)
    cmds.makeIdentity(apply=True, translate=1, rotate=1, scale=1, normal=0)


   
# Create circle control
def makeMain(controlName, x, y, z, direction):
    cmds.circle(r = 2.5, nr=(0, direction, 0), name = controlName)
    cmds.move(x, y, z, controlName)
    cmds.makeIdentity(apply=True, translate=1, rotate=1, scale=1, normal=0)



def makeCurveControl(controlName, x, y, z, rx, ry, rz):
    firstArrow = makeArrow()
    secondArrow = makeArrow()
    
    # Rotate second arrow
    cmds.rotate(0,-90,0)
    cmds.move(-3,0,3)
    largeArc = cmds.circle(name = 'largeArc', nr = (0,1,0), sweep = 90, radius = 4, center = (0,0,3))
    smallArc = cmds.circle(name = 'smallArc', nr = (0,1,0), sweep = 90, radius = 2, center = (0,0,3))

    curvedArrow = cmds.attachCurve(firstArrow, largeArc[0], smallArc[0], secondArrow, rpo = False, name = controlName)
    cmds.delete(firstArrow, largeArc[0], smallArc[0], secondArrow)
    cmds.makeIdentity(apply=True, translate=1, rotate=1, scale=1, normal=0)
    
    # Adjust control to correct position
    cmds.xform(controlName, centerPivots=True)
    cmds.scale(0.2, 0.2, 0.2)
    cmds.rotate(rx, ry, rz)
    cmds.move(x, y, z, controlName)
    
    cmds.makeIdentity(apply=True, translate=1, rotate=1, scale=1, normal=0)

    
def findControl(controlName):
    for key, value in movementDir.items():
        if value == controlName:
            return key
            
    return None  


def pntConstraint(controlName, i, j):
    if findControl(controlName) != None:
        cmds.pointConstraint(controlName, findControl(controlName), mo=True, w=1, name=f'{findControl(controlName)}Constraint', skip = (i, j))
        for i in [f'.t{i}', f'.t{j}','.rx','.ry','.rz','.sx','.sy','.sz']:
            cmds.setAttr(controlName + i, lock=True, keyable=False)
        
        
def orient(controlName, i, j):
    if findControl(controlName) != None:
        # Get the pivot position of the reference object in world space
        pivot_position = cmds.xform(findControl(controlName), query=True, translation=True, worldSpace=True)
    
        # Move the pivot of the target object to the position of the reference object
        cmds.xform(controlName, piv=pivot_position, worldSpace=True)
        cmds.orientConstraint(controlName, findControl(controlName), mo = True, name = f'{findControl(controlName)}Constraint', skip=(i, j))
        for i in ['.tx', '.ty', '.tz', f'.r{i}', f'.r{j}','.sx','.sy','.sz']:
            cmds.setAttr(controlName + i, lock=True, keyable=False)
            
        
        curve_shape = cmds.listRelatives(controlName, shapes=True, fullPath=True)
        cmds.setAttr(f'{controlName}Shape.overrideEnabled', 1)
        cmds.setAttr(f'{controlName}Shape.overrideColor', 15)
    


# =================================== CAM SETUP ==================================================
def cameraSetup():
    cam, cameraName = cmds.camera(name="renderCam_v")
    
    # Camera setup
    focalLength = cmds.distanceDimension(endPoint = (0,0,-0.45), startPoint = (0,0,-1))
    cameraGRP = cmds.parent('locator2', cam)
    cmds.rename('locator1', 'focalPoint')
    for i in ['.tx', '.ty', '.tz', '.rx','.ry','.rz','.sx','.sy','.sz']:
        cmds.setAttr(cam + i, lock=True, keyable=False)

    
    
    cmds.group(cam, name = 'pan')
    cmds.group('pan', name = 'tilt')
    cmds.group('tilt', name = 'roll')
    cmds.group('roll', name = 'dolly')
    cmds.group('dolly', name = 'truck')
    cmds.group('truck', name = 'boom')
    
    mainCtrl = makeMain('mainCTRL', 0, -1, 1, 1)
    
    # Set up dolly control
    backCtrl = makeControl('dollyCTRL', 0, 0, 3, 0, 0)
    pntConstraint('dollyCTRL', 'x', 'y')
 
    # Set up truck control
    truckControl = makeControl('truckCTRL', -1.5, 0, 1.5, 0, 90)
    pntConstraint('truckCTRL', 'y', 'z')    
        
    # Set up boom control
    boomControl = makeControl('boomCTRL', 1, 0, 1.5, 90, 0)
    pntConstraint('boomCTRL', 'x', 'z')   
     
    # Set up pan control
    panControl = makeCurveControl('panCTRL', 1, -1, -2.5, 0, -220, 0)
    orient('panCTRL', 'x', 'z')
         
    # Set up tilt control
    tiltControl = makeCurveControl('tiltCTRL', 2, -0.2, -2, 0, 135, -90)
    orient('tiltCTRL', 'y', 'z')
    
    # Set up tilt control
    tiltControl = makeCurveControl('rollCTRL', 1, 1.4, -2, 90, 0, -45)
    orient('rollCTRL', 'x', 'y')
      
            
    # Parent + Group finalize
    cmds.group(em = True, name = 'controlsGRP')
    for i, j in movementDir.items():
        cmds.parent(j, 'controlsGRP')
        

    camConstraints = 'boom'
    camControls = 'controlsGRP'
    focalPoint = 'focalPoint'
    
    for groups in [camConstraints, focalLength, camControls, focalPoint]:
        cmds.parent(groups, 'mainCTRL', shape=True)
    
     
    cmds.group('mainCTRL', name = 'renderCAM')
    cmds.delete('distanceDimension1')
    
    
    # Depth of field setup
    cmds.setAttr('renderCam_vShape1.depthOfField', 1)
    cmds.setAttr('renderCam_vShape1.aiEnableDOF', 1)
    cmds.connectAttr('distanceDimensionShape1.distance', 'renderCam_vShape1.focusDistance', force=True)
    cmds.connectAttr('distanceDimensionShape1.distance', 'renderCam_vShape1.aiFocusDistance', force=True)



# Add camera rig
def checkSetup(name):
    if cmds.objExists(name):
        print('An object called renderCAM already exists!')
    else:
        cameraSetup()
        print('renderCAM succesfully set up!')
        
        
# Remove camera rig
def checkRemove(name):
    if cmds.objExists(name):
        cmds.delete('renderCAM')
        print('renderCAM deleted!')
        
    else:
        print('renderCAM does not exist!')
                
        
# ======================== ARNOLD SETUP ===============================       
         
def setRenderer():
    cmds.setAttr('defaultRenderGlobals.currentRenderer', 'arnold', type='string')
    print('Switched to Arnold renderer.')
    
    
def setHD(width, height):
    cmds.setAttr("defaultResolution.aspectLock", 0)
    cmds.setAttr("defaultResolution.width", width)
    cmds.setAttr("defaultResolution.height", height)


def setup():
    setRenderer()
    cmds.setAttr('defaultArnoldDriver.mergeAOVs', 1) # merge AOVs
    cmds.setAttr('defaultArnoldDriver.ai_translator', 'exr', type = 'string') # file type
    cmds.setAttr('defaultRenderGlobals.imageFilePrefix', '<Scene>', type = 'string') # file name
    setHD(1920, 1080)
    addAOVs(['RGBA', 'crypto_asset', 'Z', 'N', 'P'])


def resetAOVs():
    # Delete ALL active AOVs (including light groups) and add only RGBA AOV
    aiAOV_activeAOVs = cmds.ls(type='aiAOV')
    for aov in aiAOV_activeAOVs:
        activeAOVName = cmds.getAttr('{}.name'.format(aov))
        aovs.AOVInterface().removeAOV(activeAOVName)
        
    aovs.AOVInterface().addAOV('RGBA')
    
    
def addAOVs(req_aovs):
    
    aiAOV_activeAOVs = cmds.ls(type='aiAOV')
    for name in req_aovs:   
        aiAOV_aovName = 'aiAOV_' + name
        
        # add required AOVs only if they are not active
        if aiAOV_aovName not in aiAOV_activeAOVs:
            aovs.AOVInterface().addAOV(name)
            print(aiAOV_aovName + ' AOV added.')
        else:
            print(aiAOV_aovName + ' already exists.')

def toggleSelectedAOVs(selectedAOVNames):
    # remove all AOVs with RGBA_ (light groups having RGBA_ prefix)
    aiAOV_activeAOVs = cmds.ls(type='aiAOV')
    currActiveLightGroups = []
    
    for lookDevAOVName in selectedAOVNames:
        if f"aiAOV_{lookDevAOVName}" in aiAOV_activeAOVs:
            aovs.AOVInterface().removeAOV(lookDevAOVName)
        else:
            aovs.AOVInterface().addAOV(lookDevAOVName)

            
def updateLightGroups():
    # remove all AOVs with RGBA_ (light groups having RGBA_ prefix)
    activeAOVs = cmds.ls(type='aiAOV')
    currActiveLightGroups = []
    for i in activeAOVs:
        AOVName = cmds.getAttr('{}.name'.format(i))
        if "RGBA_" in AOVName:
            aovs.AOVInterface().removeAOV(AOVName)
            

    # select lights using the defaultLightSet
    lightGroups = []
    cmds.select("defaultLightSet")
    lights = cmds.ls(selection=True)
    
    defaultAreaCounter = 1
    defaultDomeCounter = 1
    for lt in lights:
        # for unamed area light (shapes), will have aiAreaLightShape*, * will increase based on num of default/ unamed light shapes
        if "aiAreaLight" in lt:
            lightGroupName = cmds.getAttr(f"{lt[:-1]}Shape{defaultAreaCounter}.aiAov") # get the light group shape name
            print(f"{lt[:-1]}Shape{defaultAreaCounter}")
            if f"RGBA_{lightGroupName}" not in lightGroups:
                print(f"RGBA_{lightGroupName}", lightGroups)
                lightGroups.append(f"RGBA_{lightGroupName}")
            defaultAreaCounter += 1
            
        # for unamed area light (shapes), will have aiAreaLightShape*, * will increase based on num of default/ unamed light shapes
        elif "aiSkyDomeLight" in lt:
            lightGroupName = cmds.getAttr(f"{lt[:-1]}Shape{defaultDomeCounter}.aiAov") # get the light group shape name
            print(f"{lt[:-1]}Shape{defaultDomeCounter}")
            if f"RGBA_{lightGroupName}" not in lightGroups:
                print(f"RGBA_{lightGroupName}", lightGroups)
                lightGroups.append(f"RGBA_{lightGroupName}")
            defaultDomeCounter += 1
            
        # for named light
        else:
            lightGroupName = cmds.getAttr(f"{lt}Shape.aiAov")
            if f"RGBA_{lightGroupName}" not in lightGroups:
                lightGroups.append(f"RGBA_{lightGroupName}")

    # re-add back current light groups being used
    for name in lightGroups:
        aovName = 'aiAOV_' + name
        aovs.AOVInterface().addAOV(name)
        print(aovName + ' AOV added.')
    
    
    # selection clean up
    cmds.select("defaultLightSet", deselect=True)


def toggleLookDevAOVs():
    toggleSelectedAOVs(['diffuse', 'specular', 'sss', 'transmission'])


def createWindow(title, windowLabel):
    if cmds.window(title, exists=True):
        cmds.deleteUI(title)
        
    # Creates window
    cmds.window(title, w = 290, title = windowLabel, menuBar = True)
    cmds.columnLayout(adjustableColumn = True, rowSpacing = 3)
    
    
    # Render setup (Renderer, File name, file type, common AOVs, Light groups)
    cmds.text(label = "Arnold Render Setup Gizmo", fn = 'boldLabelFont', h = 30)

    cmds.text(label = "\nPrepare Render Settings (Single Frame)", font='boldLabelFont')
    cmds.button(l='Render Setup + Add Common AOVs', command = 'setup()', h = 40)
    setupDetails = "Set renderer to Arnold\nMerge AOVs\nSet file type to EXR\nSet file name to <Scene>\nSet the resolution to HD1080\nAdd common AOVs (RGBA, Z, P, N, crypto_asset)"
    cmds.text(label = "\nDoes the following:\n", al='left', font='boldLabelFont')
    cmds.text(label = setupDetails, al='left')
    
    
    cmds.text(label = "\nInit/ Update Light Groups (incl. removing unused)", font='boldLabelFont')
    cmds.button(l='Update Light Groups', command = 'updateLightGroups()', h = 40) 
    

    cmds.button(l='Toggle Lookdev AOVs', command = 'toggleLookDevAOVs()', h = 40) 
    lookdevAOVDetails = "\nToggles the following AOVs:"
    cmds.text(label = lookdevAOVDetails, font='boldLabelFont', al='left')
    cmds.text(label = "diffuse, specular, sss, transmission", al='left')
    line_separator = cmds.separator(style='in', height=10)
    
    cmds.button(l='Reset AOVs', command = 'resetAOVs()', h = 40) 
    line_separator = cmds.separator(style='in', height=10)


    # Create render Camera Rig
    cmds.text(label = "Create Camera Rig", font='boldLabelFont')
    cmds.text(label = "IMPORTANT! Do not edit the renderCAM group name.")
    cmds.button(l='Make Camera', command = "checkSetup('renderCAM')", h = 40) 
    
    
    # Remove render Camera Rig
    #cmds.text(label = "\nRemove Camera Rig")
    #cmds.button(l='Remove Camera', command = "checkRemove('renderCAM')", h = 40)

    #line_separator = cmds.separator(style='in', height=10)
    
    
    # Displays window
    cmds.showWindow(title)    



createWindow("SetupWindow", "Render Setup")
