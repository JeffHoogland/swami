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
    ELM_CALENDAR_SELECT_MODE_NONE, ELM_CALENDAR_SELECT_MODE_ONDEMAND
from efl.elementary.flip import Flip, ELM_FLIP_ROTATE_YZ_CENTER_AXIS
from efl.elementary.clock import Clock
from efl.elementary.frame import Frame

from elmextensions import StandardButton
from elmextensions import SearchableList

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

class SwamiModule(Box):
    def __init__(self, rent):
        Box.__init__(self, rent)
        self.parent = rent
        
        self.name = "Date and Time"
        self.section = "System Settings"
        self.searchData = ["clock", "timezone", "date", "system"]
        self.launchArg = "--time"
        self.button = None
        
        self.timezones = getTimeZones()
        
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

        self.tz = tz = Label(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        tz.text = "<b>%s</b>"%time.tzname[0]
        tz.show()
        
        tzframe.content = tz
        
        self.mainBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.mainBox.pack_end(cframe)
        self.mainBox.pack_end(dframe)
        self.mainBox.pack_end(tzframe)
        self.mainBox.show()
        
        self.zoneList = zoneList = SearchableList(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        zoneList.callback_item_focused_add(self.enableTZSelect)
        self.zones = []
        for tz in self.timezones:
            for each in self.timezones[tz]:
                if each not in self.zones:
                    self.zones.append(each)
        self.zones.sort(reverse=True)
        for zone in self.zones:
            zoneList.item_append(zone)
        zoneList.show()
        
        self.buttonTZSelect = buttonTZSelect = StandardButton(self, "Select", "ok", self.tzselectPressed)
        buttonTZSelect.disabled = True
        buttonTZSelect.show()
        
        buttonTZCancel = StandardButton(self, "Cancel", "close", self.tzcancelPressed)
        buttonTZCancel.show()
        
        tzBBox = Box(self, size_hint_weight = EXPAND_HORIZ, size_hint_align = FILL_BOTH)
        tzBBox.horizontal = True
        tzBBox.pack_end(buttonTZSelect)
        tzBBox.pack_end(buttonTZCancel)
        tzBBox.show()

        tzChangeBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        tzChangeBox.pack_end(zoneList)
        tzChangeBox.pack_end(tzBBox)
        tzChangeBox.show()
        
        self.flip = Flip(self, size_hint_weight=EXPAND_BOTH,
                         size_hint_align=FILL_BOTH)
        self.flip.part_content_set("front", self.mainBox)
        self.flip.part_content_set("back", tzChangeBox)
        self.flip.show()
        
        buttonBox = Box(self, size_hint_weight = EXPAND_HORIZ, size_hint_align = FILL_BOTH)
        buttonBox.horizontal = True
        
        self.buttonApply = buttonApply = StandardButton(self, "Apply Changes", "ok", self.applyPressed)
        buttonApply.disabled = True
        buttonApply.show()
        
        self.buttonSync = buttonSync = StandardButton(self, "Sync from Internet", "refresh", self.syncPressed)
        buttonSync.show()
        
        self.buttonDT = buttonDT = StandardButton(self, "Edit Date and Time", "x-office-calendar", self.editDTPressed)
        buttonDT.show()
        
        self.buttonTZ = buttonTZ = StandardButton(self, "Change Timezone", "clock", self.editTZPressed)
        buttonTZ.show()
        
        buttonReturn = StandardButton(self, "Back", "go-previous", self.returnPressed)
        buttonReturn.show()
        
        buttonBox.pack_end(buttonApply)
        buttonBox.pack_end(buttonSync)
        buttonBox.pack_end(buttonDT)
        buttonBox.pack_end(buttonTZ)
        buttonBox.pack_end(buttonReturn)
        buttonBox.show()
        
        self.pack_end(self.flip)
        self.pack_end(buttonBox)
        
    def returnPressed(self, btn):
        self.parent.returnMain()
    
    def applyPressed(self, btn):
        self.changeTime()
        self.cal.select_mode = ELM_CALENDAR_SELECT_MODE_NONE
        
        self.clock.edit_set(False)
        self.buttonApply.disabled = True
    
    def syncPressed(self, btn):
        self.runCommand('ntpdate pool.ntp.org')
    
    def editTZPressed(self, btn):
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
        self.buttonSync.disabled = True
        self.buttonDT.disabled = True
        self.buttonTZ.disabled = True
    
    def editDTPressed(self, btn):
        self.buttonApply.disabled = False
        self.cal.select_mode = ELM_CALENDAR_SELECT_MODE_ONDEMAND
        self.clock.edit_set(True)
    
    def tzselectPressed(self, btn):
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
        self.buttonSync.disabled = False
        self.buttonDT.disabled = False
        self.buttonTZ.disabled = False
        
        selectedZone = self.zoneList.selected_item_get().text
        
        self.runCommand('changetz.sh %s'%selectedZone)
        self.tz.text = "<b>%s</b>"%selectedZone
    
    def tzcancelPressed(self, btn):
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
        self.buttonSync.disabled = False
        self.buttonDT.disabled = False
        self.buttonTZ.disabled = False
    
    def enableTZSelect(self, lst, item):
        self.buttonTZSelect.disabled = False
    
    def changeTime(self):
        #print "In the change time function"
        times = list(self.clock.time_get())
        for x in times:
            if x < 10:
                times[times.index(x)] = "0%s"%x
        if not self.cal.selected_time:
            self.cal.selected_time = dt.date.today()
        self.runCommand('changetime.sh %s %s %s %s'%(self.cal.selected_time, times[0], times[1], times[2]))
    
    def runCommand(self, ourCommand):
        cmd = esudo.eSudo(ourCommand, self.parent)
