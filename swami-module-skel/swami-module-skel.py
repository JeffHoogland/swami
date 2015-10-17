#Swami skel module for the Swami Control Panel

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.icon import Icon

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

class SwamiModule(Box):
    def __init__(self, rent):
        Box.__init__(self, rent)
        self.parent = rent
        
        self.name = "Name"
        
        self.icon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        #Use FDO icons -> http://standards.freedesktop.org/icon-naming-spec/latest/ar01s04.html
        self.icon.standard_set('icon-name')
        self.icon.show()
        
        self.mainBox = Box(self, size_hint_weight = EXPAND_BOTH)
        self.mainBox.show()
        
        bkicon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        bkicon.standard_set('go-previous')
        bkicon.show()
        
        buttonReturn = Button(self, size_hint_weight = EXPAND_HORIZ)
        buttonReturn.text = "Back"
        buttonReturn.content_set(bkicon)
        buttonReturn.callback_clicked_add(self.returnPressed)
        buttonReturn.show()
        
        self.pack_end(self.mainBox)
        self.pack_end(buttonReturn)
        
    def returnPressed(self, btn):
        self.parent.returnMain()
