#Moksha Theme selector module for the Swami Control Panel

import os

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.icon import Icon
from efl import edje
from efl.edje import Edje
from efl.elementary.flip import Flip, ELM_FLIP_ROTATE_XZ_CENTER_AXIS, \
        ELM_FLIP_ROTATE_YZ_CENTER_AXIS, ELM_FLIP_INTERACTION_ROTATE
from efl.elementary.list import List, ELM_LIST_LIMIT, ELM_LIST_COMPRESS

from elmextensions import FileSelector

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

ThemePaths = [ "/usr/share/enlightenment/data/themes/",
                "%s/.e/e/themes/"%os.path.expanduser("~")]

class SwamiModule(Box):
    def __init__(self, rent):
        Box.__init__(self, rent)
        self.parent = rent
        
        self.name = "Theme Selector"
        
        self.icon = Icon(self)
        self.icon.size_hint_weight_set(EVAS_HINT_EXPAND, EVAS_HINT_EXPAND)
        self.icon.size_hint_align_set(EVAS_HINT_FILL, EVAS_HINT_FILL)
        self.icon.standard_set('preferences-desktop-theme')
        self.icon.show()
        
        self.currentPreview = None
        
        self.themeList = List(self, size_hint_weight=(0.25, 1.0), 
                    size_hint_align=FILL_BOTH, mode=ELM_LIST_COMPRESS)
        #Adds themes in the ThemePaths to the list for selection
        self.populateThemes()
        self.themeList.go()
        self.themeList.show()
        
        self.themeBox = themeBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        themeBox.horizontal_set(True)
        themeBox.pack_end(self.themeList)
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
        
        #self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
        
        self.mainBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.mainBox.pack_end(self.flip)
        self.mainBox.show()
        
        bkicon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        bkicon.standard_set('go-previous')
        bkicon.show()
        
        buttonReturn = Button(self, size_hint_weight=EXPAND_HORIZ)
        buttonReturn.text = "Back"
        buttonReturn.content_set(bkicon)
        buttonReturn.callback_clicked_add(self.returnPressed)
        buttonReturn.show()
        
        self.pack_end(self.mainBox)
        self.pack_end(buttonReturn)
    
    def populateThemes(self):
        for ourPath in ThemePaths:
            for k in os.walk(ourPath):
                for themeFile in k[2]:
                    self.addTheme(themeFile, ourPath)
    
    def addTheme(self, themeFile, ourPath):
        edjeObj = Edje(self.evas, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        
        try:
            edjeObj.file_set("%s/%s"%(ourPath, themeFile), "moksha/preview")
        except:
            edjeObj.file_set("%s/%s"%(ourPath, themeFile), "e/desktop/background")
        
        edjeObj.show()
        
        listItem = self.themeList.item_append("%s"%themeFile, edjeObj, callback=self.themeSelected)
    
    def themeSelected(self, obj, item=None):
        edjeObj = item.object_get()
        
        if self.currentPreview:
            self.themeBox.unpack(self.currentPreview)
        
        self.themeBox.pack_end(edjeObj)
        self.currentPreview = edjeObj
    
    def fileSelected(self, fs, ourFile):
        if ourFile[-4:] == ".edj":
            self.importTheme(ourFile)
        else:
            print "Please select a theme file"
    
    def importTheme(self, themeFile):
        edjeObj = Edje(self.evas, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        try:
            edjeObj.file_set(themeFile, "moksha/preview")
        except:
            edjeObj.file_set(themeFile, "e/desktop/background")
        #Accessing global data
        print edje.file_data_get(themeFile, "gtk-theme")
        
        edjeObj.show()
        self.mainBox.pack_end(edjeObj)
        
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
    
    def returnPressed(self, btn):
        self.parent.returnMain()
    
    def shutDownFS(self, arg):
        self.fs.shutdown()
