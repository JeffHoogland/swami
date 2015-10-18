#Moksha Theme selector module for the Swami Control Panel

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.icon import Icon
from efl import edje
from efl.edje import Edje

from elmextensions import FileSelector

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

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
        
        self.fs = fs = FileSelector(self.parent, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        fs.setMode("Open")
        fs.show()

        #need to do this to shutdown threading for the file selector
        self.parent.callback_delete_request_add(self.shutDownFS)
        
        fs.callback_activated_add(self.fileSelected)
        
        self.mainBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.mainBox.pack_end(fs)
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
    
    def fileSelected(self, fs, ourFile):
        if ourFile[-4:] == ".edj":
            self.importTheme(ourFile)
        else:
            print "Please select a theme file"
    
    def importTheme(self, themeFile):
        edjeObj = Edje(self.parent.evas, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        edjeObj.file_set(themeFile, "moksha/preview")
        #Accessing global data
        print edje.file_data_get(themeFile, "gtk-theme")
        
        edjeObj.show()
        self.mainBox.pack_end(edjeObj)
    
    def returnPressed(self, btn):
        self.parent.returnMain()
    
    def shutDownFS(self, arg):
        self.fs.shutdown()
