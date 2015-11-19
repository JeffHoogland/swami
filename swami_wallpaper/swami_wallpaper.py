#Swami skel module for the Swami Control Panel

import os
import webbrowser
import shutil
import neet
import time
import dbus
import shutil

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.icon import Icon
from efl.elementary.scroller import Scroller

from efl import ecore

from efl import edje
from efl.edje import Edje
from efl.elementary.flip import Flip, ELM_FLIP_ROTATE_YZ_CENTER_AXIS
from efl.elementary.list import List, ELM_LIST_LIMIT, ELM_LIST_COMPRESS

from elmextensions import FileSelector
from elmextensions import StandardButton

UserHome = os.path.expanduser("~")

OutputDir="%s/.e/e/backgrounds"%UserHome

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

WallPaths = [ "/usr/share/enlightenment/data/backgrounds/",
                "%s/.e/e/backgrounds/"%UserHome]

class SwamiModule(Box):
    def __init__(self, rent):
        Box.__init__(self, rent)
        self.parent = rent
        
        self.name = "Wallpaper"
        self.section = "Appearance"
        self.searchData = ["wallpaper", "appearance", "look"]
        self.launchArg = "--wallpaper"
        self.button = None
        
        self.icon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        #Use FDO icons -> http://standards.freedesktop.org/icon-naming-spec/latest/ar01s04.html
        self.icon.standard_set('wallpaper')
        self.icon.show()
        
        self.foundWalls = []
        
        self.currentPreview = None
        self.selectedWall = None
        
        self.flip = Flip(self, size_hint_weight=EXPAND_BOTH,
                         size_hint_align=FILL_BOTH)
        
        wallBox = Box(self.flip, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        wallBox.horizontal_set(True)
        
        self.previewBox = previewBox = Scroller(wallBox, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        previewBox.show()
        
        self.wallList = List(self, size_hint_weight=(0.35, 1.0), 
                    size_hint_align=FILL_BOTH, mode=ELM_LIST_COMPRESS)
        #Adds walls in the WallPaths to the list for selection
        self.populateWalls()
        self.wallList.go()
        self.wallList.show()
        
        wallBox.pack_end(self.wallList)
        wallBox.pack_end(self.previewBox)
        wallBox.show()
        
        self.fs = fs = FileSelector(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        fs.setMode("Open")
        fs.show()

        #need to do this to shutdown threading for the file selector
        self.parent.callback_delete_request_add(self.shutDownFS)
        
        fs.callback_activated_add(self.fileSelected)
        
        # Flip object has the file selector on one side
        #   and the GUI on the other
        self.flip.part_content_set("front", wallBox)
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
        
        buttonImport = StandardButton(self, "Import Wallpaper", "wallpaper", self.importPressed)
        buttonImport.show()
        
        buttonReturn = StandardButton(self, "Back", "go-previous", self.returnPressed)
        buttonReturn.show()
        
        buttonBox.pack_end(buttonApply)
        #buttonBox.pack_end(buttonWeb)
        buttonBox.pack_end(buttonImport)
        buttonBox.pack_end(buttonReturn)
        buttonBox.show()
        
        self.pack_end(self.mainBox)
        self.pack_end(buttonBox)
    
    def populateWalls(self):
        for ourPath in WallPaths:
            for k in os.walk(ourPath):
                for wallFile in k[2]:
                    self.addWall(wallFile, ourPath)
    
    def addWall(self, wallFile, ourPath):
        '''edjeObj = Edje(self.evas, size_hint_weight=EXPAND_BOTH, 
                        size_hint_align=FILL_BOTH)
        edjeObj.file_set("%s/%s"%(ourPath, wallFile), "e/desktop/background")
        edjeObj.show()'''
        
        listItem = self.wallList.item_append("%s"%wallFile, callback=self.wallSelected)
        listItem.data["filePath"] = "%s%s"%(ourPath, wallFile)
        listItem.selected_set(True)
        
        self.foundWalls.append("%s%s"%(ourPath, wallFile))
        
        self.wallSelected(None, listItem)
    
    def wallSelected(self, obj, item):
        #self.previewBox.clear()
        
        #edjeObj = Layout(self.previewBox, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        
        edjeObj = Edje(self.previewBox.evas, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        
        filePath = item.data["filePath"]
        edjeObj.file_set(filePath, "e/desktop/background")
        edjeObj.show()
        
        self.previewBox.content_set(edjeObj)
        self.currentPreview = edjeObj
        self.selectedWall = filePath
    
    def fileSelected(self, fs, ourPath):
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
        
        #move the file to temp dir / rename it so we can work around a issue with spaces in file names
        tmpCount = 1
        while os.path.isfile("/tmp/swamiwall_%s"%tmpCount):
            tmpCount += 1
        
        shutil.copy2(ourPath, '/tmp/swamiwall_%s'%tmpCount)
        
        time.sleep(1)
        
        ourFile = os.path.splitext(os.path.basename(ourPath))[0].replace(" ", "")
        
        ecore.Exe('convertimage.sh %s %s'%('/tmp/swamiwall_%s'%tmpCount, ourFile))
        
        time.sleep(1)
        self.addWall("%s.edj"%ourFile, "%s/.e/e/backgrounds/"%UserHome)
    
    def returnPressed(self, btn):
        self.parent.returnMain()
        
    def importPressed(self, btn):
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
    
    def applyPressed(self, btn):
        #Dbus call to stop Moksha from fighting with our changes
        bus = dbus.SessionBus()
        obj = bus.get_object('org.enlightenment.wm.service', '/org/enlightenment/wm/RemoteObject')
        iface = dbus.Interface(obj, dbus_interface='org.enlightenment.wm.Config')
        iface.SaveBlock()
        
        #Update Moksha Theme
        #Get existing profile
        eProfileFile = neet.EETFile()
        eProfileFile.importFile("%s/.e/e/config/profile.cfg"%UserHome, "-x")
        eProfile = eProfileFile.readValue()
        
        eCFG = neet.EETFile()
        eCFG.importFile("%s/.e/e/config/%s/e.cfg"%(UserHome, eProfile))
        ewallData = eCFG.readValue((("value", "desktop_default_background"),))
        
        ewallData.data = self.selectedWall
        #print ewallData
        eCFG.saveData()
        
        #Give Moksha control of the config data again
        iface.Load()
        iface.SaveRelease()
    
    def shutDownFS(self, arg):
        self.fs.shutdown()
