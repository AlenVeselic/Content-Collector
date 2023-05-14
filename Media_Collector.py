# -*- coding: utf-8 -*-

# Content collector

# An application meant to serve in accumulating and filtering content from select boorus and reddit.

# TODO: singleElementView - the delete content key press is not limited to the filtration folder,
# therefore allowing you to delete any content although the delete button is not present in the ui.
# Minimum FIX:Limit that to the assigned folders
# UPGRADE: set up an actual filtration mode in place of the current
# one.

# BUG: If you click on the send to button, cancel, and then try to send to the previously chosen folder. The button prompts you to chose 
# a new folder anyway, because your previous action wiped the currently selected folder without reseting the ui.
# MINUMUM FIX: Make Send to only wipe the currently selected folder only when a new folder has been chosen.
# UPGRADE: ADD Dropdown menu that holds previously chosen folders. Add folders every time a new folder is chosen in send to.
# Allow filtration folder list customization in settings. Acknowledge these files when checking for duplicates when scraping.

# BUG: single element view - gif and video player controls extend into the left and right buttons making the slider useless once it reaches 
# the move right button.

# TODO: Sort booru tags alphabetically. Seems like, although there is a progress bar, it still feels weird that they don't go in an alphabetical order.

# UPGRADE: Add booru tag categorization. Maybe add relationships, so that a certain tag always excludes it's tags in relation and that tags in a relation have a run order character>franchise.
# Add a tag blacklist.
# For reddit add a user blacklist.

# TODO: Optimize autoplaying ContentWidgets. Maybe take less frames for the autoplaying widgets. Maybe add style to an autoplayable widget frame, that plays the viedo on hover. Being able to barely 
# support 20 autoplayable widgets and having that also lag the other the entire app is a problem. Maybe deactivated autoplaying videos in singleelementview.

# TODO: Introduce a working logging system and hide unnecessary logs.

# UPGRADE: Pagination
# UPGRADE: Infinite scroll pagination. Check which widgets are active in the viewports and deactivated obscured ones. Reloading widgets in view should not be an issue, just don't reload the widget dimensions
# if they had already been loaded.

from PyQt5 import QtWidgets
from PyQt5.QtMultimedia import *
from pathlib import Path
import sys

from dotenv import load_dotenv

from views.uiWrapper.UiWithResizeLogic import UIWithResizeLogic

            
if __name__ == "__main__":
    load_dotenv()
    app = QtWidgets.QApplication(sys.argv)
    qss = Path('default.qss').read_text()
    app.setStyleSheet(Path('default.qss').read_text())
    MainWindow = UIWithResizeLogic()
    MainWindow.show()
    sys.exit(app.exec_())
