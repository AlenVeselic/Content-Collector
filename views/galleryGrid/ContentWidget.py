from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from shared.ClickableLabel import ClickableLabel
from shared.ClickableVideoWidget import ClickableVideoWidget
from shared.functions import calculateElementHeight

from views.galleryGrid.functions.imageThread import loadThread, setupThread

from views.uiWrapper.UiWithResizeLogic import UIWithResizeLogic
from constants.ContentWidgetTypes import ContentWidgetTypes

class ContentWidget(QWidget):
    def __init__(self, widgetPath, fileName, contentDirectory, mainWindow, contentTrigger, imageTrigger, widgetNumber, parent=None):
        QWidget.__init__(self, parent)
        self.id = widgetNumber
        self.loaded = False

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0,0,0,0)

        self.widgetPath: str = widgetPath
        self.fileName: str = fileName
        self.contentDirectory: str = contentDirectory
        self.mainWindow: UIWithResizeLogic = mainWindow

        self.pixmap = QPixmap()
        self.label = ClickableLabel()
        self.label.setContentsMargins(0, 0, 0, 0)

        self.setObjectName("contentWidget")

        self.videoPlayers = []
        self.playlists = []
        self.counter = 0
        self.setContent()
        self.setContentsMargins(0,0,0,0)
        if self.type == ContentWidgetTypes.IMAGE:
            self.loadImageThread(self.id)
        elif self.type == ContentWidgetTypes.GIF:
            self.loadGifThread()
        elif self.type == ContentWidgetTypes.VIDEO:
            self.loadVideoThread()

    def setContent(self):

        if not self.widgetPath.endswith(('.mp4', '.gif')):
            #print("Image " + self.fileName + " is being processed." + " " + str(len(self.mainWindow.content) + 1))
            self.type = ContentWidgetTypes.IMAGE
            self.runImageThread()

        elif self.widgetPath.endswith('.mp4'):
            #print("Video " + self.fileName + " is being processed. " + " " + str(len(self.mainWindow.content) + 1))
            self.type = ContentWidgetTypes.VIDEO
            self.label = ClickableVideoWidget()

            self.runVideoThread()

            self.mainWindow.vidNumber += 1
        else:
            #print("Gif " + self.fileName + " is being processed. " + " " + str(len(self.mainWindow.content) + 1))
            self.type = ContentWidgetTypes.GIF
            self.runGifThread()

    def loadImageThread(self, widgetNumber):
        if(widgetNumber == self.id):
            self.imageLoadingThread = loadThread(self.widgetPath, "image")
            self.imageLoadingThread.imageLoaded.connect(self.setLoadedImage)
            self.imageLoadingThread.start()
    
    def loadGifThread(self):
        self.gifLoadingThread = loadThread(self.widgetPath, "gif")
        self.gifLoadingThread.gifLoaded.connect(self.setLoadedGif)
        self.gifLoadingThread.start()
    
    def loadVideoThread(self):
        self.videoLoadingThread = loadThread(self.widgetPath, "video")
        self.videoLoadingThread.videoLoaded.connect(self.setLoadedVideo)
        self.videoLoadingThread.start()
    
    def setLoadedImage(self, image, ratio):

        basicWidth = int(self.mainWindow.ui.centralwidget.width()/4)

        pixmap = QPixmap()
        pixmap.convertFromImage(image)

        self.label.setPixmap(pixmap)

        widgetHeight = calculateElementHeight(basicWidth, self.label)
        self.label.setContentsMargins(0,0,0,0)
        self.label.setMaximumHeight(widgetHeight)
        self.setMaximumHeight(widgetHeight)
        self.loaded = True
        
    def setLoadedGif(self, gifData: QByteArray):
        self.buffer = QBuffer()
        self.buffer.setData(gifData)
        self.gif = QMovie()
        self.gif.setCacheMode(self.gif.CacheMode.CacheAll)
        self.gif.setDevice(self.buffer)

        self.label.setMovie(self.gif)

        self.gif.start()

        basicWidth = int(self.mainWindow.ui.centralwidget.width()/4)

        widgetHeight = calculateElementHeight(basicWidth, self.label)

        self.label.setMaximumHeight(widgetHeight)

        self.label.setScaledContents(True)

        self.loaded = True

    def setLoadedVideo(self, video: QMediaContent):

        videoPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoPlayers.append(videoPlayer)

        videoBuffer = QMediaContent(video)

        playlist = QMediaPlaylist()
        
        self.playlists.append(playlist)
        self.playlists[self.counter].addMedia(videoBuffer)
        self.playlists[self.counter].setPlaybackMode(QMediaPlaylist.Loop)

        self.videoPlayers[self.counter].setPlaylist(self.playlists[self.counter])
        self.videoPlayers[self.counter].setVolume(0)
        self.videoPlayers[self.counter].setVideoOutput(self.label)
        self.videoPlayers[self.counter].play()

        try:
            ratio = (videoBuffer.canonicalResource().resolution().height()/videoBuffer.canonicalResource().resolution().width())
        except ZeroDivisionError:
            print("ratio calculation failed")
            ratio = 1
        basicWidth = int(self.mainWindow.ui.centralwidget.width()/4)
        self.label.setMaximumHeight(basicWidth*ratio)

        self.setVideo(self.label)

        self.loaded = True

    def setImage(self, newWidget: ClickableLabel):
        self.centralwidget = newWidget
        self.horizontalLayout.addWidget(newWidget)
        self.setLayout(self.horizontalLayout)

    def setGif(self, newWidget: ClickableLabel):
        self.centralwidget = newWidget
        self.horizontalLayout.addWidget(newWidget)
        self.setLayout(self.horizontalLayout)
    
    def setVideo(self, newWidget: ClickableVideoWidget):
        self.centralwidget = newWidget
        self.horizontalLayout.addWidget(newWidget)
        self.setLayout(self.horizontalLayout)
    
    def runImageThread(self):
        self.imageThread = setupThread(self.contentDirectory, self.widgetPath, self.fileName, self.mainWindow.ui, self.mainWindow, self.pixmap, self.label, "image")
        self.imageThread.imageSignal.connect(self.setImage)
        self.imageThread.start()
    
    def runGifThread(self):
        self.gifThread = setupThread(self.contentDirectory, self.widgetPath, self.fileName, self.mainWindow.ui, self.mainWindow, self.pixmap, self.label, "gif")
        self.gifThread.imageSignal.connect(self.setGif)
        self.gifThread.start()
    
    def runVideoThread(self):
        self.videoThread = setupThread(self.contentDirectory ,self.widgetPath, self.fileName, self.mainWindow.ui, self.mainWindow, self.pixmap, self.label, "video")
        self.videoThread.imageSignal.connect(self.setVideo)
        self.videoThread.start()
    def resizeEvent(self, event):
        if hasattr(self, "centralwidget") and self.loaded == True:
            #print("Resizing!")
            newWidgetHeight = calculateElementHeight(self.parentWidget().width(), self.centralwidget)
            if(self.type == ContentWidgetTypes.GIF):
                
                self.gif = QMovie(self.widgetPath)
                self.gif.setCacheMode(self.gif.CacheMode.CacheAll)

                self.label.setMovie(self.gif)

                self.gif.start()

                newGifSize = QSize(self.parentWidget().width(), newWidgetHeight)
                self.gif.setScaledSize(newGifSize)
            self.setMaximumHeight(newWidgetHeight)
            self.centralwidget.setMaximumHeight(newWidgetHeight)