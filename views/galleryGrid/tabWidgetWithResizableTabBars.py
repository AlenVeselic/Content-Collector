from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from pathlib import Path

import logging
logging.basicConfig(format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s', level=logging.DEBUG)

class tabWidgetWithResizableTabBar(QWidget):
    def __init__(self, tabs, parent, stylePath, resizeTrigger = None):
        super(QWidget, self).__init__(parent)

        self.logPrefix = "[Tab Widget]"

        self.stylePath = stylePath

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        self.tabs.setUsesScrollButtons(False)
        self.setTabs(tabs)

        self.tabs.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.tabs.setCurrentIndex(0)

        self.tabs.currentChanged.connect(self.tabChanged)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._set_tabs_width()

    def showEvent(self, event):
        super().showEvent(event)
        self._set_tabs_width()

    def _set_tabs_width(self):
        tabs_count = self.tabs.count()
        tabs_width = self.tabs.width()
        if tabs_count == 3:
            tab_width = (tabs_width / tabs_count) + 1
        else:
            tab_width = tabs_width / tabs_count


        logging.info(f"Current path: {Path.cwd()}")
        css = "%s QTabBar::tab {width: %spx}" % (self.stylePath.read_text(), tab_width)
        self.tabs.setStyleSheet(css)
    
    def setTabs(self, tabs):
        for tab in tabs:
            self.tabs.addTab(tab["widget"], tab["name"])

    def tabChanged(self, index: int):

        currentWidget = self.tabs.currentWidget()
        currentChildren = currentWidget.children()
        try:
            refreshChild = currentChildren[1].refresh()
        except AttributeError as e:
            if "object has no attribute 'refresh'" in str(e):
                logging.info(f"Unimplemented refresh function on view")
            else:
                logging.info(f"Unknown attribute error {e}")
