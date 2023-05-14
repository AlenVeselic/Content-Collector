from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class GridWidget(QWidget):

    def __init__(self, resizeTrigger: pyqtSignal, parent=None):
        QWidget.__init__(self, parent)

        resizeTrigger.connect(self.resizeSelf)
    
    def resizeSelf(self):
        print("Resize grid!")
        containerWidth = self.parentWidget().parentWidget().parentWidget().width()
        print("Parent widget width:" + str(containerWidth))
        self.setMaximumWidth(containerWidth)
        print("New Width: " + str(containerWidth))