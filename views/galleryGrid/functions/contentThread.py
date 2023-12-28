from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from views.galleryGrid.functions.gridGeneration import generateContentThreaded

class contentThread(QThread):
    content = pyqtSignal(str, str, str)

    def __init__(self, contentDirectory, mainWindow, pagesAvailableSignal, currentPage, contentFilenames = None):
        QThread.__init__(self)
        self.contentDirectory = contentDirectory
        self.mainWindow = mainWindow
        self.contentFilenames = contentFilenames
        self.pagesAvailableSignal = pagesAvailableSignal
        self.currentPage = currentPage
        
    def run(self):
        generateContentThreaded(self.contentDirectory, self.mainWindow, self.content, self.pagesAvailableSignal, self.currentPage, self.contentFilenames)