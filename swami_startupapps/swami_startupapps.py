#Moksha startup applications module for the Swami Control Panel

import os
from gtk import icon_theme_get_default

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.entry import Entry
from efl.elementary.icon import Icon
from efl.elementary.image import Image
from efl.elementary.list import List, ListItem
from efl.elementary.frame import Frame
from efl.elementary.flip import Flip, ELM_FLIP_ROTATE_YZ_CENTER_AXIS
from efl.elementary.popup import Popup

from elmextensions import StandardButton, SearchableList

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

UserHome = os.path.expanduser("~")

IconTheme = icon_theme_get_default()

StartupApplicationsFile = "%s/.e/e/applications/startup/.order"%UserHome

StartupCommandsFile = "%s/.e/e/applications/startup/startupcommands"%UserHome

ApplicationPaths = [ "/usr/share/applications/",
                "%s/.local/share/applications/"%UserHome]

class SwamiModule(Box):
    def __init__(self, rent):
        Box.__init__(self, rent)
        self.parent = rent
        
        #This appears on the button in the main swmai window
        self.name = "Startup Applications"
        #The section in the main window the button is added to
        self.section = "Applications"
        #Search terms that this module should appear for
        self.searchData = ["startup", "command", "applications", "apps"]
        #Command line argument to open this module directly
        self.launchArg = "--startupapps"
        #Should be none by default. This value is used internally by swami
        self.button = None
        
        self.icon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        #Use FDO icons -> http://standards.freedesktop.org/icon-naming-spec/latest/ar01s04.html
        self.icon.standard_set('system-run')
        self.icon.show()
        
        self.mainBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.mainBox.show()
        
        buttonBox = Box(self, size_hint_weight = EXPAND_HORIZ, size_hint_align = FILL_BOTH)
        buttonBox.horizontal = True
        
        buttonApply = StandardButton(self, "Apply", "ok", self.applyPressed)
        buttonApply.show()
        
        buttonFlip = StandardButton(self, "Startup Commands", "preferences-system", self.flipPressed)
        buttonFlip.show()
        
        buttonReturn = StandardButton(self, "Back", "go-previous", self.returnPressed)
        buttonReturn.show()
        
        buttonBox.pack_end(buttonApply)
        buttonBox.pack_end(buttonFlip)
        buttonBox.pack_end(buttonReturn)
        buttonBox.show()
        
        startupApplications = []
        
        with open(StartupApplicationsFile) as startupFile:
            for line in startupFile:
                startupApplications.append(line.rstrip())
        
        desktopFiles = []
        
        for ourPath in ApplicationPaths:
            desktopFiles += [os.path.join(dp, f) for dp, dn, filenames in os.walk(ourPath) for f in filenames if os.path.splitext(f)[1] == '.desktop']
        
        self.startupList = startupList = List(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        
        self.applicationsList = applicationsList = SearchableList(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)

        startupToAdd = []
        applicationsToAdd = []

        for d in desktopFiles:
            with open(d) as desktopFile:
                fileName = d.split("/")[-1]
                icon = None
                for line in desktopFile:
                    if line[:5] == "Name=":
                        name = line[5:][:-1]
                    
                    if line[:5] == "Icon=":
                        icon = line[5:]
                    
                
                if icon:
                    iconInfo = IconTheme.lookup_icon(icon.strip(), 48, 0)

                    if iconInfo:
                        iconObj = Image(self, file=iconInfo.get_filename(), size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
                        iconInfo = iconInfo.get_filename()
                    else:
                        iconObj = Icon(self, standard="preferences-system", size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
                else:
                    iconObj = Icon(self, standard="preferences-system", size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
                
                if fileName in startupApplications:
                    startupToAdd.append([name, iconObj, fileName, iconInfo])
                else:
                    applicationsToAdd.append([name, iconObj, fileName, iconInfo])
        
        startupToAdd.sort()
        applicationsToAdd.sort()
        
        for s in startupToAdd:
            ourItem = startupList.item_append(s[0], s[1])
            ourItem.data["file"] = s[2]
            ourItem.data["icon"] = s[3]
            #ourItem.append_to(startupList)
            #startupList.item_append(ourItem)
        
        for a in applicationsToAdd:
            ourItem = applicationsList.item_append(a[0], a[1])
            ourItem.data["file"] = a[2]
            ourItem.data["icon"] = a[3]
            #ourItem.append_to(applicationsList.ourList)
            #applicationsList.item_append(a[0], a[1])
        
        startupList.callback_clicked_double_add(self.startupAppRemove)
        applicationsList.callback_clicked_double_add(self.startupAppAdd)
        
        startupList.go()
        startupList.show()
        applicationsList.show()
        
        startupFrame = Frame(self, size_hint_weight = EXPAND_BOTH, size_hint_align=FILL_BOTH)
        startupFrame.text = "Startup Applications"
        startupFrame.content_set(startupList)
        startupFrame.show()
        
        otherFrame = Frame(self, size_hint_weight = EXPAND_BOTH, size_hint_align=FILL_BOTH)
        otherFrame.text = "Other Applications"
        otherFrame.content_set(applicationsList)
        otherFrame.show()
        
        self.mainBox.pack_end(startupFrame)
        self.mainBox.pack_end(otherFrame)
        
        self.backBox = Box(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.backBox.show()
        
        self.commandsList = commandsList = List(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        
        with open(StartupCommandsFile) as scf:
            for line in scf:
                if line.rstrip()[-3:] == "| \\":
                    commandsList.item_append(line.rstrip()[:-3])
                else:
                    commandsList.item_append(line.rstrip())
                
        commandsList.callback_clicked_right_add(self.commandRightClicked)
        
        commandsList.go()
        commandsList.show()
        
        commandBox = Box(self, size_hint_weight=EXPAND_HORIZ, size_hint_align=(1, 0.5))
        commandBox.horizontal = True
        commandBox.show()
        
        self.newCommandEntry = newCommandEntry = Entry(self, size_hint_weight = EXPAND_HORIZ, size_hint_align = FILL_BOTH)
        newCommandEntry.single_line = True
        newCommandEntry.text = "<i>Type command here</i>"
        newCommandEntry.data["default text"] = True
        newCommandEntry.callback_clicked_add(self.entryClicked)
        newCommandEntry.show()
        
        newCommandButton = StandardButton(self, "Add Command", "add", self.newCmdPressed)
        newCommandButton.show()
        
        delCommandButton = StandardButton(self, "Delete Command", "exit", self.delCmdPressed)
        delCommandButton.show()
        
        commandBox.pack_end(newCommandButton)
        commandBox.pack_end(delCommandButton)
        
        newCommandFrame = Frame(self, size_hint_weight = EXPAND_HORIZ, size_hint_align = FILL_BOTH)
        newCommandFrame.text = "Add Startup Command:"
        newCommandFrame.content_set(newCommandEntry)
        newCommandFrame.show()
        
        self.backBox.pack_end(commandsList)
        self.backBox.pack_end(newCommandFrame)
        self.backBox.pack_end(commandBox)
        
        self.flip = Flip(self, size_hint_weight=EXPAND_BOTH,
                         size_hint_align=FILL_BOTH)
        self.flip.part_content_set("front", self.mainBox)
        self.flip.part_content_set("back", self.backBox)
        self.flip.show()
        
        self.pack_end(self.flip)
        self.pack_end(buttonBox)
    
    def startupAppRemove(self, lst, itm):
        text = itm.text
        dataFile = itm.data["file"]
        dataIcon = itm.data["icon"]
        itm.delete()
        
        if dataIcon:
            iconObj = Image(self, file=dataIcon, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        else:
            iconObj = Icon(self, standard="preferences-system", size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        
        ourItem = self.applicationsList.item_append(text, iconObj)
        ourItem.data["file"] = dataFile
        ourItem.data["icon"] = dataIcon
    
    def startupAppAdd(self, lst, itm):
        text = itm.text
        dataFile = itm.data["file"]
        dataIcon = itm.data["icon"]
        itm.delete()
        
        if dataIcon:
            iconObj = Image(self, file=dataIcon, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        else:
            iconObj = Icon(self, standard="preferences-system", size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        
        ourItem = self.startupList.item_append(text, iconObj)
        ourItem.data["file"] = dataFile
        ourItem.data["icon"] = dataIcon
        self.startupList.go()
    
    def flipPressed(self, btn):
        if btn.text == "Startup Commands":
            btn.text = "Startup Applications"
        else:
            btn.text = "Startup Commands"
        
        self.flip.go(ELM_FLIP_ROTATE_YZ_CENTER_AXIS)
    
    def commandRightClicked(self, lst, itm):
        self.delCmdMenu.move(1, 1)
        self.delCmdMenu.show()
    
    def entryClicked(self, entry):
        if entry.data["default text"]:
            entry.data["default text"] = False
            entry.text = ""
    
    def newCmdPressed(self, btn):
        self.commandsList.item_append(self.newCommandEntry.text)
        self.newCommandEntry.text = ""
        self.commandsList.go()
    
    def delCmdPressed(self, btn):
        selectedCommand = self.commandsList.selected_item_get()
        selectedCommand.delete()
    
    def applyPressed(self, btn):
        with open(StartupApplicationsFile, 'w') as saf:
            for i in self.startupList.items_get():
                saf.write(i.data["file"])
                saf.write("\n")
        
        with open(StartupCommandsFile, 'w') as scf:
            lastI = self.commandsList.last_item_get()
            for i in self.commandsList.items_get():
                if i != lastI:
                    scf.write(i.text + " | \\ \n")
                else:
                    scf.write(i.text)
        
        p = Popup(self, size_hint_weight=EXPAND_BOTH, timeout=3.0)
        p.text = "Changes Successfully Applied"
        p.show()
    
    def returnPressed(self, btn):
        self.parent.returnMain()
