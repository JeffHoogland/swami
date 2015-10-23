#Moksha Theme selector module for the Swami Control Panel

import os
import webbrowser
import shutil
import neet
import time

from efl import ecore

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, EVAS_ASPECT_CONTROL_BOTH
from efl import elementary
from efl.elementary.box import Box
from efl.elementary.icon import Icon
from efl.elementary.image import Image

from efl import edje
from efl.edje import Edje
from efl.elementary.flip import Flip, ELM_FLIP_ROTATE_XZ_CENTER_AXIS, \
        ELM_FLIP_ROTATE_YZ_CENTER_AXIS, ELM_FLIP_INTERACTION_ROTATE
from efl.elementary.list import List, ELM_LIST_LIMIT, ELM_LIST_COMPRESS

from elmextensions import FileSelector
from elmextensions import StandardButton
from elmextensions import StandardPopup

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

ThemeURL = "http://www.bodhilinux.com/softwaregroup/themes/"
ThemePaths = [ "/usr/share/enlightenment/data/themes/",
                "%s/.e/e/themes/"%os.path.expanduser("~")]

class SwamiModule(Box):
    def __init__(self, rent):
        Box.__init__(self, rent)
        self.parent = rent
        
        self.name = "Theme Selector"
        self.section = "Appearance"
        self.searchData = ["theme", "gtk", "elementary", "elm", "gnome",
                    "appearance", "look"]
        self.button = None
        
        self.icon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.icon.standard_set('preferences-desktop-theme')
        self.icon.show()
        
        self.foundThemes = []
        
        self.currentPreview = None
        self.selectedTheme = None
        
        
        self.previewBox = previewBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        #Doesn't seem to do anything
        #previewBox.size_hint_aspect_set(EVAS_ASPECT_CONTROL_BOTH, 16, 9)
        previewBox.show()
        
        self.themeList = List(self, size_hint_weight=(0.25, 1.0), 
                    size_hint_align=FILL_BOTH, mode=ELM_LIST_COMPRESS)
        #Adds themes in the ThemePaths to the list for selection
        self.populateThemes()
        self.themeList.go()
        self.themeList.show()
        
        themeBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        themeBox.horizontal_set(True)
        themeBox.pack_end(self.themeList)
        themeBox.pack_end(self.previewBox)
        themeBox.show()
        
        self.fs = fs = FileSelector(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        fs.setMode("Open")
        fs.show()

        #need to do this to shutdown threading for the file selector
        self.parent.callback_delete_request_add(self.shutDownFS)
        
        fs.callback_activated_add(self.fileSelected)
        
        # Flip object has the file selector on one side
        #   and the GUI on the other
        self.flip = Flip(self, size_hint_weight=EXPAND_BOTH,
                         size_hint_align=FILL_BOTH)
        self.flip.part_content_set("front", themeBox)
        self.flip.part_content_set("back", self.fs)
        self.flip.show()
        
        fs.callback_cancel_add(lambda o: self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS))
        
        #self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
        
        self.mainBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.mainBox.pack_end(self.flip)
        self.mainBox.show()
        
        buttonBox = Box(self, size_hint_weight = EXPAND_HORIZ, size_hint_align = FILL_BOTH)
        buttonBox.horizontal = True
        
        buttonApply = StandardButton(self, "Apply Selected", "ok", self.applyPressed)
        buttonApply.show()
        
        buttonWeb = StandardButton(self, "Get Themes", "applications-internet", self.webPressed)
        buttonWeb.show()
        
        #buttonGTK = StandardButton(self, "GTK Theme", "preferences-desktop-gnome", self.gtkPressed)
        #buttonGTK.show()
        
        #buttonElm = StandardButton(self, "Elementary Theme", "", self.elmPressed)
        #buttonElm.show()
        
        buttonImport = StandardButton(self, "Import Theme", "preferences-desktop-theme", self.importPressed)
        buttonImport.show()
        
        buttonReturn = StandardButton(self, "Back", "go-previous", self.returnPressed)
        buttonReturn.show()
        
        buttonBox.pack_end(buttonApply)
        buttonBox.pack_end(buttonWeb)
        #buttonBox.pack_end(buttonGTK)
        #buttonBox.pack_end(buttonElm)
        buttonBox.pack_end(buttonImport)
        buttonBox.pack_end(buttonReturn)
        buttonBox.show()
        
        self.pack_end(self.mainBox)
        self.pack_end(buttonBox)
    
    def populateThemes(self):
        for ourPath in ThemePaths:
            for k in os.walk(ourPath):
                for themeFile in k[2]:
                    self.addTheme(themeFile, ourPath)
    
    def addTheme(self, themeFile, ourPath):
        edjeObj = Edje(self.evas, size_hint_weight=EXPAND_BOTH, 
                        size_hint_align=FILL_BOTH)
        
        try:
            edjeObj.file_set("%s/%s"%(ourPath, themeFile), "moksha/preview")
        except:
            edjeObj.file_set("%s/%s"%(ourPath, themeFile), "e/desktop/background")
        
        edjeObj.show()
        
        listItem = self.themeList.item_append("%s"%themeFile, edjeObj, callback=self.themeSelected)
        listItem.data["filePath"] = "%s%s"%(ourPath, themeFile)
        listItem.selected_set(True)
        
        self.foundThemes.append("%s%s"%(ourPath, themeFile))
        
        self.themeSelected(None, listItem)
    
    def themeSelected(self, obj, item):
        self.previewBox.clear()
        
        edjeObj = Edje(self.evas, size_hint_weight=EXPAND_BOTH, 
                size_hint_align=FILL_BOTH)
        filePath = item.data["filePath"]
        
        try:
            edjeObj.file_set(filePath, "moksha/preview")
        except:
            edjeObj.file_set(filePath, "e/desktop/background")
        
        edjeObj.show()
        
        self.previewBox.pack_end(edjeObj)
        self.currentPreview = edjeObj
        self.selectedTheme = filePath
    
    def fileSelected(self, fs, ourFile):
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
        ourPath, themeFile = os.path.split(ourFile)
        if ourFile[-4:] == ".edj":
            shutil.copy2(ourFile, "%s/.e/e/themes"%os.path.expanduser("~"))
            self.addTheme(themeFile, "%s/.e/e/themes/"%os.path.expanduser("~"))
        else:
            errorPop = StandardPopup(self, "%s does not appear to be a valid theme file."%themeFile, 'dialog-warning')
            errorPop.show()
    
    def returnPressed(self, btn):
        self.parent.returnMain()
    
    def webPressed(self, btn):
        webbrowser.open(ThemeURL)
        try:
            os.wait()
        except:
            pass
    
    def gtkPressed(self, btn):
        pass
    
    def elmPressed(self, btn):
        pass
    
    def importPressed(self, btn):
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
    
    def applyPressed(self, btn):
        #Accessing global data
        #print edje.file_data_get(themeFile, "gtk-theme")
        #The current selected theme path - self.selectedTheme
        
        #Update Moksha Theme
        #eProfile = "bodhi" #ideally we should check what profile they are using need to figure out how to do that
        eProfileFile = neet.EETFile()
        eProfileFile.importFile("%s/.e/e/config/profile.cfg"%os.path.expanduser("~"), "-x")
        eProfile = eProfileFile.readValue()
        
        eCFG = neet.EETFile()
        eCFG.importFile("%s/.e/e/config/%s/e.cfg"%(os.path.expanduser("~"), eProfile))
        ethemeData = eCFG.readValue((("list", "themes"), ("item", "E_Config_Theme",  "category" , "theme"), ("value", "file")))
        
        ethemeData.data = self.selectedTheme
        #print ethemeData.data
        eCFG.saveData()
        #eCFG.saveData("/home/jeff/written_e.cfg")
        time.sleep(1.5)
        
        #Update elm theme order
        #elmProfile = "standard" #same as eProfile - shouldn't just assume
        elmProfileFile = neet.EETFile()
        elmProfileFile.importFile("%s/.elementary/config/profile.cfg"%os.path.expanduser("~"), "-x")
        elmProfile = elmProfileFile.readValue()
        
        elmCFG = neet.EETFile()
        elmCFG.importFile("%s/.elementary/config/%s/base.cfg"%(os.path.expanduser("~"), elmProfile))
        
        themeData = elmCFG.readValue((("value", "theme"),))
        
        themeName = edje.file_data_get(self.selectedTheme, "elm-theme")
        
        themeData.data = "%s:MokshaRadiance:default"%themeName
        
        elmCFG.saveData()
        
        #Restart the desktop to have theme changes take effect
        cmd = ecore.Exe("enlightenment_remote -restart")
        #Flush Elm settings
        elementary.Configuration.all_flush
        
    def shutDownFS(self, arg):
        self.fs.shutdown()
