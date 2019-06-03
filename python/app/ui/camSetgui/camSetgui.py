#### use this tool to set camera attributs from presets stored in shotgun
# https://nozon.shotgunstudio.com
# There's no attribut type detection yet, The attribut setting will work for "float" and "int" attribut type.
# below, the fieldQueryDict is used to both query shotgun field from the camera entity and translate shotgun field code to maya attribut name. 
# If the field in shotgun is empty, the UI won't display values otherwise the UI will even allow editing in addition of setting maya attributs.  
# You can add field to shotgun camera entity, but you have to fill tje fieldQuery dict unless the UI won't detect and display the new shotgun fields

#To run the UI#
#>import maya_tools.sg_cameraPreset 
#>maya_tools.sg_cameraPreset.launch()




try :
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui
    _signal = QtCore.Signal 


except :
    from PyQt4 import QtGui, QtCore
    _signal = QtCore.pyqtSignal

import maya.OpenMayaUI as mui
import maya.cmds as cmds




class WidgetAttribut(QtGui.QWidget) :
    def __init__(self, maxAttrSize, attributName, attributValue):
        self.attrName = attributName
        QtGui.QWidget.__init__(self) 
        
        labelQ = QtGui.QLabel(attributName)
        maxWidth   = labelQ.fontMetrics().boundingRect(maxAttrSize ).width()
        emptyWidth = maxWidth -  labelQ.fontMetrics().boundingRect(labelQ.text() ).width()
        
        self.intFieldQ = QtGui.QLineEdit(attributValue)
        self.intFieldQ.setValidator(QtGui.QDoubleValidator(  self.intFieldQ))
        
        widgetLayoutQ = QtGui.QHBoxLayout()
        widgetLayoutQ.setContentsMargins(0,0,0,0)
        widgetLayoutQ.addWidget(labelQ)
        widgetLayoutQ.addSpacing(emptyWidth)

        widgetLayoutQ.addWidget(self.intFieldQ)
        widgetLayoutQ.addStretch()
        self.setLayout(widgetLayoutQ)
        
    def getValue(self):
        return self.attrName,self.intFieldQ.text()
        
        
        
        
class WidgetCamera(QtGui.QWidget):
    def __init__(self, cameraDataDict):
        QtGui.QWidget.__init__(self) 
        
        self.cameraDataDict = cameraDataDict
        
        self.dynamicWidgetList = []
        widgetLayoutQ = QtGui.QVBoxLayout()
        self.setLayout(widgetLayoutQ)
        

        editCamLayout    = QtGui.QHBoxLayout()
        
        editCameraFieldLabelQ           = QtGui.QLabel('Camera to set : ')
        self.editCameraFieldQ           = QtGui.QLineEdit("")
        self.editCameraFiledPickButtonQ = QtGui.QPushButton("Get Selected")
        editCamLayout.addWidget(editCameraFieldLabelQ)
        editCamLayout.addWidget(self.editCameraFieldQ    )
        editCamLayout.addWidget(self.editCameraFiledPickButtonQ)
        editCamLayout.addStretch()

        comboLayout = QtGui.QHBoxLayout()
        cameraNameLabelQ          = QtGui.QLabel("Camera Name : ")
        self.cameraNameComboBoxQ  = QtGui.QComboBox()
        self.cameraNameComboBoxQ.addItems(cameraDataDict.keys())
        
        comboLayout.addWidget(cameraNameLabelQ)
        comboLayout.addWidget(self.cameraNameComboBoxQ)
        comboLayout.addStretch()
        
        widgetLayoutQ.addLayout(editCamLayout)
        widgetLayoutQ.addLayout(comboLayout)
        
        
        
        self.dynamicLayout = QtGui.QVBoxLayout()
        self.dynamicLayout.setContentsMargins(0,0,0,0)
        
        
        widgetLayoutQ.addLayout(self.dynamicLayout)
    
    
        self.redrawCameraWidget(self.cameraNameComboBoxQ.currentIndex())
    
        self.connectUI()
       
    
       
    def connectUI(self):
        self.editCameraFiledPickButtonQ.clicked.connect(self.setSelectedCamera)
        self.cameraNameComboBoxQ.currentIndexChanged.connect(self.redrawCameraWidget)
    
    
    
    def clearLayout(self, layoutQ):
        self.dynamicWidgetList = []
        while layoutQ.count():
            child = layoutQ.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())
                
                
    def fillLayout(self, layoutQ, cameraData):
        maxAttr = ""
        self.dynamicWidgetList = []
        for attr in  cameraData.keys() :
            if len(attr) > len(maxAttr) :
                maxAttr=attr
      
        for attr in  cameraData.keys() :
            dynWidgetQ = WidgetAttribut(maxAttr, attr, str(cameraData[attr]))
            layoutQ.addWidget(dynWidgetQ)
            self.dynamicWidgetList.append(dynWidgetQ)
        layoutQ.addStretch()
    
    
    def applyValues( self):
        import traceback
        
        for attrWidgetQ in self.dynamicWidgetList :
            param,value = attrWidgetQ.getValue() 
            try :
                cmds.setAttr(str(self.editCameraFieldQ.text()) +"."+param, float(value) )
            except :
                
                print "Can't set to : '"+ self.editCameraFieldQ.text() +"."+param + "' value  '"  +   str(value)  +"'"
                print traceback.format_exc()   

    ############## SLOTS ##############
        
    def setSelectedCamera(self) :
        mayaSelectionList = cmds.ls(sl=True)
        if  mayaSelectionList:
            self.editCameraFieldQ.setText(mayaSelectionList[0])


    def redrawCameraWidget(self, index) :
        cameraPresetCode = self.cameraNameComboBoxQ.itemText(index)
        
        cameraData = self.cameraDataDict[str(cameraPresetCode)]
        self.clearLayout(self.dynamicLayout)
        
        
        self.fillLayout(self.dynamicLayout, cameraData )

class Example(QtGui.QWidget):
   
    
    def __init__(self):
        #Init my main window, and pass in the maya main window as it's parent
        QtGui.QWidget.__init__(self)  
        

        fieldQueryDict = { "sg_focallength" : "focalLength",   
                   "sg_horizontalfilmaperture" : "horizontalFilmAperture",  
                   "sg_verticalfilmaperture" : "verticalFilmAperture",
                   "sg_filmfit" : "filmFit",
                   "sg_nearclipplane" : "nearClipPlane",
                   } 


        self.cameraDataDict = self.queryDataBaseShotgun(fieldQueryDict)
        import traceback
        
        try :

            mainLayout = QtGui.QVBoxLayout()
            self.link = QtGui.QLabel("<a href=\"https://nozon.shotgunstudio.com/page/4577\">  Shotgun camera page : https://nozon.shotgunstudio.com/page/4577</a>")
            self.link.mousePressEvent = self.openWebLink
            self.cameraWidget = WidgetCamera(self.cameraDataDict)
            self.applyButtonQ = QtGui.QPushButton("Apply Camera settings")
            mainLayout.addWidget(self.link)
            mainLayout.addWidget(self.cameraWidget )
            mainLayout.addWidget(self.applyButtonQ)
            
            self.setLayout(mainLayout)
            

            self.applyButtonQ.clicked.connect(self.cameraWidget.applyValues)
            self.show()
        except :
            print traceback.format_exc()

    def openWebLink(self, event ):
        import webbrowser
        webbrowser.open('https://nozon.shotgunstudio.com/page/4577')

    def queryDataBaseXML(self) :
        pass
             
    def queryDataBaseShotgun(self, fieldQueryDict = {} ) :
        
        try :
            from shotgun_api3 import Shotgun
        except :
            import sys
            sys.path.append('\\\\server01\\shared\\sharedPython2.6\\site-packages_win64\\')
            from shotgun_api3 import Shotgun
        
        SERVER_PATH = "https://nozon.shotgunstudio.com"
        SCRIPT_NAME = 'CamQuery'     
        SCRIPT_KEY = '9c3d3ff0e384e8312328164f337bd62199ee19651c2e8ad44dbd85e98f78ebff'
        
        print "Make shotgun connection",
        sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
    
        print "to query shotgun camera datas."
        self.cameraDataDict = {}
    
    
        for cameraData in sg.find("CustomNonProjectEntity03",[], ["code"]+fieldQueryDict.keys() ) :
            self.cameraDataDict[ cameraData["code"] ]={}
    
            for sg_field in fieldQueryDict.keys() :
                if cameraData[sg_field] :
                    self.cameraDataDict[ cameraData["code"] ][fieldQueryDict[sg_field] ] = cameraData[sg_field]
    
        return self.cameraDataDict
            


