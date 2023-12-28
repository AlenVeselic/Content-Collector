from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *

from shared.ClickableLabel import ClickableLabel
from shared.ClickableVideoWidget import ClickableVideoWidget
from views.galleryGrid.functions.gridGeneration import generateImageWidgetThreaded, generateGifWidgetThreaded, generateVideoWidgetThreaded

class setupThread(QThread):
    imageSignal = pyqtSignal(ClickableLabel)
    videoSignal = pyqtSignal(ClickableVideoWidget)

    def __init__(self, arrayPath, path, file, mainWindow, app, pixmap: QPixmap, label: ClickableLabel, type):
        QThread.__init__(self)
        self.arrayPath = arrayPath
        self.path = path
        self.file = file
        self.mainWindow = mainWindow
        self.app = app
        self.pixmap = pixmap
        self.label = label
        self.type = type
        

    def run(self):
        if(self.type == "image"):
            generateImageWidgetThreaded(self.arrayPath, self.path, self.file, self.mainWindow, self.app, self.pixmap, self.label, self.imageSignal)
        elif(self.type == "gif"):
            generateGifWidgetThreaded(self.arrayPath, self.path, self.file, self.app, self.label, self.imageSignal)
        elif self.type == "video":
            generateVideoWidgetThreaded(self.arrayPath, self.path, self.file, self.app.vidNumber, self.app.ui.videoplayers, self.app.ui.playlists, self.app.ui, self.app, self.label, self.videoSignal)
        else:
            print("undefined content type")

class loadThread(QThread):
    imageLoaded = pyqtSignal(QImage, int)
    gifLoaded = pyqtSignal(QByteArray)
    videoLoaded = pyqtSignal(QMediaContent)

    def __init__(self, path, type):
        QThread.__init__(self)
        self.path = path
        self.type = type
    
    def run(self):
        if self.type == "image":
            #print("Loading image: " + self.path)
            loadImageThreaded(self.path, self.imageLoaded)
        elif self.type == "gif":
            loadGifThreaded(self.path, self.gifLoaded)
        elif self.type == "video":
            loadVideoThreaded(self.path, self.videoLoaded)
        else:
            print("Unknown content type")

def loadImageThreaded(imagePath, loadedSignal):
    
    pixmap = QImage(imagePath)

    pixmapRect = pixmap.rect()

    try:
        elementRatio = pixmapRect.height()/pixmapRect.width()
        loadedSignal.emit(pixmap, elementRatio)
    except ZeroDivisionError as e:
        print("Error" + str(e))
        elementRatio = 1

def loadGifThreaded(gifPath, loadedSignal):

    file = QFile(gifPath)
    file.open(QFile.OpenModeFlag.ReadOnly)
    byteArray = file.readAll()
    loadedSignal.emit(byteArray)
    file.close()

def loadVideoThreaded(videoPath, loadedSignal):
    
    video = QMediaContent(QUrl.fromLocalFile(videoPath))
    loadedSignal.emit(video)




        
