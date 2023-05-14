from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class ColumnWidget(QWidget):

    def __init__(self, resizeTrigger = None, parent=None):
        QWidget.__init__(self, parent)

        self.isLastInRow: bool = False
        self.row = 0
        
    def resizeSelf(self):
        print("Resize column!")
        containerWidth = self.parentWidget().parentWidget().width()
        print("Parent widget width:" + str(containerWidth))
        newWidth = containerWidth/5
        if newWidth < 100:
            newWidth = 100
        self.setMaximumWidth(newWidth)
        print("New Width: " + str(newWidth))