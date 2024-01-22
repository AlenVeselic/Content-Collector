from PyQt5 import QtWidgets
from views.singleContent.singleElement import singleElementView

class ClickableLabel(QtWidgets.QLabel):

    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.mainWindow = ""
    
    def setElement(self, directory, filePath, file):
        self.element = file
        self.elementPath = filePath
        self.directoryPath = directory

    def mouseReleaseEvent(self, event):
        singleView = singleElementView()
        singleView.directory = self.directoryPath
        singleView.contentPath = self.elementPath
        singleView.content = self.element
        self.mainWindow.chLayout(singleView)