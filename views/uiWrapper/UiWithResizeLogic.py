import os, psycopg2
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from views.galleryGrid.gallery import galleryView
from views.singleElement import singleElementView
from views.scraper.scraperView import scraperView

from views.galleryGrid.functions.gridGeneration import createGrid, resizeGrid
from shared.functions import calculateElementHeight

from views.galleryGrid.functions.contentThread import contentThread


class UIWithResizeLogic(QMainWindow):
    content = []
    todaysPicks = []

    initContent = pyqtSignal()
    loadContent = pyqtSignal(int)
    resizeTrigger = pyqtSignal()

    currentWidget = 0

    destination = ""

    maxPages = 0
    pagesAvailable = pyqtSignal(int)
    updatePagesLabel = pyqtSignal(str)

    currentContentFilenames = None
    currentChosenDirectory = ""

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = galleryView()
        self.ui.setDirectory = self.setDirectory
        self.ui.chLayout = self.chLayout
        self.ui.setupUi(self, False)
        self.pagesAvailable.connect(self.setMaxPages)
        self.ui.nextPageButton.clicked.connect(self.nextPage)
        self.ui.previousPageButton.clicked.connect(self.previousPage)
        self.updatePagesLabel.connect(self.ui.updatePages)
        
        self.currentGridColumnNumber = 0
        self.vidNumber = 0
        self.lastSetDirectoryFolder = ""
        self.destinationFolders = []

        if os.environ.get("DATABASE_ENABLED") == "True":
            print("Initializing database connection")
            self.db = psycopg2.connect(
                database=os.environ.get("DATABASE"),
                user=os.environ.get("DATABASE_USER"),
                password=os.environ.get("DATABASE_PASSWORD"),
                host=os.environ.get("DATABASE_HOST"),
                port=os.environ.get("DATABASE_PORT"),
            )
                
    def chLayout(self, newUi):
        if isinstance(newUi, singleElementView):
            nextUi = newUi
            
            nextUi.imageArrayPath = newUi.directory
            if nextUi.imageArrayPath != "Today's Picks":
                nextUi.imageArray: list[str] = os.listdir(newUi.directory)
                nextUi.imageArray.sort(key=lambda filename: os.path.getctime(os.path.join(newUi.directory, filename)))
            else:
                nextUi.imageArray: list[str] = self.todaysPicks
            nextUi.contentAmount = len(nextUi.imageArray)

            nextUi.imageIndex = nextUi.imageArray.index(str(newUi.content))
            nextUi.setEnabled(True)
            self.ui.baseWindow.addWidget(nextUi)
            self.ui.baseWindow.setCurrentWidget(nextUi)
            nextUi.setContent(newUi.contentPath)
            
        if isinstance(newUi, scraperView):
            nextUi = newUi
            print("Scraper view")
            nextUi.setEnabled(True)
            self.ui.baseWindow.addWidget(nextUi)
            self.ui.baseWindow.setCurrentWidget(nextUi)
    
    def setDirectory(self, act, directory=0, contentFilenames = None, currentPage = 0):
        self.content = []
        self.currentGridColumnNumber = 0
        if self.lastSetDirectoryFolder == "":
            initDir = str(Path.home())
        else:
            initDir = self.lastSetDirectoryFolder
        print(str(directory))
        if contentFilenames != None:
            print(f"Received content filenames: {contentFilenames}")
        if directory == 0 and contentFilenames == None:
            folder = QFileDialog.getExistingDirectory(self.ui.menuFile, "Choose directory", initDir)
            self.currentChosenDirectory = folder
            lastSlashIndex = folder.rfind("/")
            containingFolder = folder[:lastSlashIndex]
            self.lastSetDirectoryFolder = containingFolder
        else:
            folder = directory
            self.ui.imageArrayPath = folder

        if folder or contentFilenames != None:
            newWidge = createGrid(self)
            newWidge.setObjectName(u"scrollAreaWidgetContents")
            self.ui.scrollArea.setWidget(newWidge)
            if folder == 0:
                folder = "Today's Picks"
            self.ui.statusbar.showMessage(folder)

            if contentFilenames == None:
                self.generateContent(folder, currentPage)
            else:
                self.currentContentFilenames = contentFilenames
                self.generateContent(folder, currentPage, contentFilenames)

    def generateContent(self, folder, currentPage, contentFilenames = None):
        self.contentGenerationThread = contentThread(folder, self, self.pagesAvailable, currentPage, contentFilenames)
        self.contentGenerationThread.content.connect(self.newContent)
        self.contentGenerationThread.start()

    def newContent(self, widgetPath, fileName, contentDirectory):

        newWidget = ContentWidget(widgetPath, fileName, contentDirectory, self, self.initContent, self.loadContent, len(self.content))

        newWidget.setProperty("class", "empty")
        newWidget.setMinimumWidth(100)

        column = self.ui.scrollArea.widget().layout().itemAt(self.currentGridColumnNumber).widget()
        column.setContentsMargins(0, 0, 0, 0)

        if self.ui.scrollArea.width() > 1000:
            numberOfColumns = 8
            maxWidth = self.ui.scrollArea.width()/numberOfColumns

            finalItemMargin = 75
        else:
            numberOfColumns = 6
            maxWidth = self.ui.scrollArea.width()/numberOfColumns
            finalItemMargin = 65

        if maxWidth > column.minimumWidth():
            basicWidth = maxWidth
        else:
            basicWidth = column.minimumWidth()  
    
        lineWidth = basicWidth*(numberOfColumns-2)

        #print("Column: " + str(self.currentGridColumnNumber))
        
        if self.currentGridColumnNumber >= numberOfColumns - 2:
            self.currentGridColumnNumber = 0
        else:
            self.currentGridColumnNumber += 1
        

        
        element = newWidget

        element.mainWindow = self
        
        if column.width() < basicWidth:
            height = calculateElementHeight(basicWidth, element)
        else:
            height = calculateElementHeight(int(self.ui.scrollArea.width() - lineWidth - finalItemMargin), element)
        
        if isinstance(element, QLabel) and element.movie() != None:
            if column.width() < basicWidth:
                element.movie().setScaledSize(QSize(basicWidth, height))
            else:
                element.movie().setScaledSize(QSize(int(self.ui.scrollArea.width() - lineWidth - finalItemMargin), height)) 

            print("Height result: " + str(height))
            element.setMaximumHeight(height)

            
        column.layout().addWidget(element)

        self.content.append(newWidget)
        self.ui.retranslateUi(self)


    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            if isinstance(self.ui.baseWindow.currentWidget(), singleElementView) or isinstance(self.ui.baseWindow.currentWidget(), scraperView):
                if isinstance(self.ui.baseWindow.currentWidget(), singleElementView):
                    for widgetIndex in range(self.ui.baseWindow.currentWidget().imageLayout.count()):
                        widgetToRemove = self.ui.baseWindow.currentWidget().imageLayout.itemAt(widgetIndex).widget()
                        self.ui.baseWindow.currentWidget().imageLayout.removeWidget(widgetToRemove)
                        widgetToRemove.setParent(None)

                self.ui.baseWindow.setCurrentWidget(self.ui.centralwidget)
        if key == Qt.Key_A:
            self.initContent.emit()

    def paginateContent(self):

        print("Loading more")

        for i in range(len(self.content)):
            self.loadContent.emit(self.currentWidget)
            if self.currentWidget == len(self.content):
                print("All has been loaded")
                allLoaded = True
                break
            self.currentWidget += 1
                
    def setMaxPages(self, pages):
        
        self.maxPages = pages
        print(f"Page update: {self.ui.currentPage}/{self.maxPages}")
        self.ui.availablePages = self.maxPages
        self.ui.pagesLabel.setText(f"{self.ui.currentPage}/{self.maxPages}")
        self.ui.pagesLabel.repaint()


    def nextPage(self):
        self.ui.currentPage = self.ui.currentPage + 1
        
        print(f"Page update: {self.ui.currentPage}/{self.maxPages}")
        self.updatePagesLabel.emit(f"{self.ui.currentPage}/{self.maxPages}")
        self.setDirectory("act", self.currentChosenDirectory, self.currentContentFilenames, self.ui.currentPage)

    
    def previousPage(self):
        self.ui.currentPage = self.ui.currentPage - 1
        
        print(f"Page update: {self.ui.currentPage}/{self.maxPages}")
        self.updatePagesLabel.emit(f"{self.ui.currentPage}/{self.maxPages}")
        self.setDirectory("act", self.currentChosenDirectory, self.currentContentFilenames, self.ui.currentPage)

    def resizeEvent(self, event):
        if not isinstance(self.ui.baseWindow.currentWidget(), singleElementView) and not self.content == None:
            QMainWindow.resizeEvent(self, event)
            self.resizeOverride()

    def resizeOverride(self):
            print("Window has been resized")
            print(f"Scrollarea size {self.ui.scrollArea.size()}")
            print(f"gallery tab size {self.ui.gallery_tab.size()}")
            print(f"tab widget size {self.ui.tabWidgetWithResizableTabBars.size()}")
            print(f"central widget size {self.ui.centralwidget.size()}")
            print(f"basewindow {self.ui.baseWindow.size()}")
            
            self.resizeTrigger.emit()

            resizeGrid(self)

from views.galleryGrid.ContentWidget import ContentWidget