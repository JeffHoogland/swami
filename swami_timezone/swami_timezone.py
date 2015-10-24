#Swami skel module for the Swami Control Panel

import time
import dateutil.tz as dtz
import pytz
import datetime as dt
import collections
import esudo.esudo as esudo

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.icon import Icon
from efl.elementary.label import Label
from efl.elementary.calendar_elm import Calendar, \
    ELM_DAY_MONDAY, ELM_DAY_THURSDAY, ELM_DAY_SATURDAY, \
    ELM_CALENDAR_UNIQUE, ELM_CALENDAR_DAILY, ELM_CALENDAR_WEEKLY, \
    ELM_CALENDAR_MONTHLY, ELM_CALENDAR_ANNUALLY, \
    ELM_CALENDAR_SELECT_MODE_NONE, ELM_CALENDAR_SELECT_MODE_ONDEMAND
from efl.elementary.clock import Clock
from efl.elementary.frame import Frame

from elmextensions import StandardButton

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

def getTimeZones():
    result=collections.defaultdict(list)
    for name in pytz.common_timezones:
        timezone=dtz.gettz(name)
        now=dt.datetime.now(timezone)
        offset=now.strftime('%z')
        abbrev=now.strftime('%Z')
        result[offset].append(name)
        result[abbrev].append(name)    
    return result

def searchList(text, lst):
    for item in lst:
        if text.lower() in item.lower()[:len(text)]:
            return lst.index(item)
    return 0

class SwamiModule(Box):
    def __init__(self, rent):
        Box.__init__(self, rent)
        self.parent = rent
        
        self.name = "Date and Time"
        self.section = "System Settings"
        self.searchData = ["clock", "timezone", "date", "system"]
        self.launchArg = "--time"
        self.button = None
        
        self.icon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        #Use FDO icons -> http://standards.freedesktop.org/icon-naming-spec/latest/ar01s04.html
        self.icon.standard_set('clock')
        self.icon.show()
        
        cframe = Frame(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        cframe.text = "Current Time"
        cframe.show()

        self.clock = clock = Clock(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        clock.show_seconds_set(True)
        clock.show_am_pm_set(True)
        clock.show()
        
        cframe.content = clock
        
        dframe = Frame(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        dframe.text = "Current Day"
        dframe.show()

        self.cal = cal = Calendar(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        cal.select_mode = ELM_CALENDAR_SELECT_MODE_NONE
        cal.show()
        
        dframe.content = cal
        
        tzframe = Frame(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        tzframe.text = "Current Timezone"
        tzframe.show()

        tz = Label(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        tz.text = "<b>%s</b>"%time.tzname[0]
        tz.show()
        
        tzframe.content = tz
        
        self.mainBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.mainBox.pack_end(cframe)
        self.mainBox.pack_end(dframe)
        self.mainBox.pack_end(tzframe)
        self.mainBox.show()
        
        buttonBox = Box(self, size_hint_weight = EXPAND_HORIZ, size_hint_align = FILL_BOTH)
        buttonBox.horizontal = True
        
        self.buttonApply = buttonApply = StandardButton(self, "Apply Changes", "ok", self.applyPressed)
        buttonApply.disabled = True
        buttonApply.show()
        
        buttonSync = StandardButton(self, "Sync from Internet", "refresh", self.syncPressed)
        buttonSync.show()
        
        buttonDT = StandardButton(self, "Edit Date and Time", "x-office-calendar", self.editDTPressed)
        buttonDT.show()
        
        buttonTZ = StandardButton(self, "Change Timezone", "clock", self.editTZPressed)
        buttonTZ.show()
        
        buttonReturn = StandardButton(self, "Back", "go-previous", self.returnPressed)
        buttonReturn.show()
        
        buttonBox.pack_end(buttonApply)
        buttonBox.pack_end(buttonSync)
        buttonBox.pack_end(buttonDT)
        buttonBox.pack_end(buttonTZ)
        buttonBox.pack_end(buttonReturn)
        buttonBox.show()
        
        self.pack_end(self.mainBox)
        self.pack_end(buttonBox)
        
    def returnPressed(self, btn):
        self.parent.returnMain()
    
    def applyPressed(self, btn):
        pass
    
    def syncPressed(self, btn):
        self.runCommand('ntpdate pool.ntp.org')
    
    def editTZPressed(self, btn):
        pass
    
    def editDTPressed(self, btn):
        self.buttonApply.disabled = False
        self.cal.select_mode = ELM_CALENDAR_SELECT_MODE_ONDEMAND
        self.clock.edit_set(True)
    
    def runCommand(self, ourCommand):
        cmd = esudo.eSudo(ourCommand, self.parent)
