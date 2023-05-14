from PyQt5 import QtCore

from scraper_scripts import booruScraper

class scraperThread(QtCore.QThread):
    text = QtCore.pyqtSignal(str)
    clear = QtCore.pyqtSignal(str)
    mediaProgress = QtCore.pyqtSignal(int)
    overallProgress = QtCore.pyqtSignal(int)
    shelve = r"./Data/CollectorData" # Set this value in a centralized location

    def __init__(self, destination):
        QtCore.QThread.__init__(self)
        self.destination = destination

    def run(self):
        booruScraper.main(self.destination, self.shelve , self.text, self.clear, self.mediaProgress, self.overallProgress)
