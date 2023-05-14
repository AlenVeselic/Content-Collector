from PyQt5 import QtMultimediaWidgets

from views.singleElement import singleElementView

# TODO: Make parent class for clickable label and this

class ClickableVideoWidget(QtMultimediaWidgets.QVideoWidget):
    def __init__(self, parent=None):
        QtMultimediaWidgets.QVideoWidget.__init__(self, parent)
        self.mainWindow = ""
    
    def set(self, directory, filePath, file):
        self.element = file
        self.elementPath = filePath
        self.directoryPath = directory

    def mouseReleaseEvent(self, event):
        singleView = singleElementView()
        singleView.directory = self.directoryPath
        singleView.contentPath = self.elementPath
        singleView.content = self.element
        self.mainWindow.chLayout(singleView)
