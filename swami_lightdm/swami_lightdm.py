#Swami skel module for the Swami Control Panel

LightDMConf = "/etc/lightdm/lightdm.conf"
XsessionsDir = "/usr/share/xsessions"

import esudo.esudo as esudo

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.icon import Icon
from efl.elementary.frame import Frame
from efl.elementary.entry import Entry

from elmextensions import StandardButton

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

class SwamiModule(Box):
    def __init__(self, rent):
        Box.__init__(self, rent)
        self.parent = rent
        
        #This appears on the button in the main swmai window
        self.name = "Light DM"
        #The section in the main window the button is added to
        self.section = "System Settings"
        #Search terms that this module should appear for
        self.searchData = ["lightdm", "autologin", "login", "display"]
        #Command line argument to open this module directly
        self.launchArg = "--lightdm"
        #Should be none by default. This value is used internally by swami
        self.button = None
        
        self.icon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        #Use FDO icons -> http://standards.freedesktop.org/icon-naming-spec/latest/ar01s04.html
        self.icon.standard_set('video-display')
        self.icon.show()
        
        self.mainBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.mainBox.show()
        
        self.config = {}
        
        with open(LightDMConf) as f:
            for line in f:
                #Sections start with [ - such as [SeatDefaults]
                if line[0] != "[":
                    setting, value = line.replace("\n", "").split("=")
                    
                    e = Entry(self)
                    e.single_line_set(True)
                    e.text = value
                    e.show()
                    
                    f = Frame(self, size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
                    f.text = setting
                    f.content = e
                    f.show()
                    
                    self.mainBox.pack_end(f)
                    
                    self.config[setting] = f
        
        buttonBox = Box(self, size_hint_weight = EXPAND_HORIZ, size_hint_align = FILL_BOTH)
        buttonBox.horizontal = True
        
        buttonSave = StandardButton(self, "Save Changes", "ok", self.savePressed)
        buttonSave.show()
        
        buttonReturn = StandardButton(self, "Back", "go-previous", self.returnPressed)
        buttonReturn.show()
        
        buttonBox.pack_end(buttonSave)
        buttonBox.pack_end(buttonReturn)
        buttonBox.show()
        
        self.pack_end(self.mainBox)
        self.pack_end(buttonBox)
    
    def savePressed(self, btn):
        dataList = ["[SeatDefaults]\n"]
        for s in self.config:
            f = self.config[s]
            dataList.append("%s=%s\n"%(f.text, f.content_get().text))
        
        with open("/tmp/lightdm.conf", 'w') as f:
            for item in dataList:
                f.write(item)
        
        self.runCommand('mv -f /tmp/lightdm.conf %s'%LightDMConf)
    
    def returnPressed(self, btn):
        self.parent.returnMain()
    
    def runCommand(self, ourCommand):
        cmd = esudo.eSudo(ourCommand, self.parent)
