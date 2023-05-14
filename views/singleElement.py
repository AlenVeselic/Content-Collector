
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from shared.GifPlayer import GifPlayer
from shared.VideoPlayer import VideoPlayer
from shared.getSizeAdjustedToContainer import getSizeAdjustedToContainer
from constants.mediaExtensions import imageExtensions, videoExtension, gifExtension
from pathlib import Path
from send2trash import send2trash
import os, shutil

# TODO: Make view folder
# TODO. Move draggableScrollArea class out of view file
# TODO: Collect destination folder and have a dropdown menu that allows you to pick which folder you
# want to send to, minimizing repetitive destination input
# TODO: Style toolbar buttons
# BUG: Videos get clipped at the bottom

class draggableScrollArea(QScrollArea):
    def __init__(self, parent=None):
        QScrollArea.__init__(self, parent)
        self.mMouseDragging = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus) # Allows using button clicks in main view instead of soaking them up

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if(event.button() == Qt.MouseButton.LeftButton):
            self.mMouseDragging = True
            self.mLastMouseDragLocation = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if(self.mMouseDragging):
            delta = QPoint(event.pos() - self.mLastMouseDragLocation)
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.mLastMouseDragLocation = event.pos()
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if(event.button() == Qt.MouseButton.LeftButton):
            self.mMouseDragging = False
            self.mLastMouseDragLocation = event.pos()
            self.setCursor(Qt.CursorShape.OpenHandCursor)
    
    def wheelEvent(self, a0: QWheelEvent) -> None:
        print("Nothing")

class singleElementView(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.imageIndex = 0
        self.imageArrayPath = r""
        self.imageArray = ""
        self.contentAmount = len(self.imageArray)
        self.updateParent = False
        self.loaded = False

        self.playlist = []
        self.videoPlayer = []

        self.scale = 1

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setContentsMargins(0,0,0,0)

        self.centralwidget = QWidget(self)

        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())

        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setLayoutDirection(Qt.LeftToRight)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)

        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"upperToolbar")
        self.widget_2.setEnabled(True)

        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())

        self.widget_2.setSizePolicy(sizePolicy1)
        self.widget_2.setSizeIncrement(QSize(0, 0))
        self.widget_2.setAutoFillBackground(False)

        self.horizontalLayout = QHBoxLayout(self.widget_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(9, -1, -1, -1)

        self.backButton = QPushButton(self.widget_2)
        self.backButton.setObjectName(u"backButton")
        self.backButton.clicked.connect(self.goBack)

        self.horizontalLayout.addWidget(self.backButton)

        self.widget_3 = QWidget(self.widget_2)
        self.widget_3.setObjectName(u"widget_3")

        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())

        self.widget_3.setSizePolicy(sizePolicy2)

        # TODO: Remove zoom gui buttons or introduce a slider
        self.zoomOutButton = QPushButton(self.widget_3)
        self.zoomOutButton.setObjectName(u"ZoomOut")
        self.zoomOutButton.setGeometry(QRect(10, 0, 75, 23))
        self.zoomInButton = QPushButton(self.widget_3)
        self.zoomInButton.setObjectName(u"ZoomIn")
        self.zoomInButton.setGeometry(QRect(100, 0, 75, 23))

        self.deleteButton = QPushButton(self.widget_3)
        self.deleteButton.setObjectName(u"DeleteButton")
        self.deleteButton.setGeometry(QRect(190, 0, 75, 23))

        self.sendToButton = QPushButton(self.widget_3)
        self.sendToButton.setObjectName(u"SendToButton")
        self.sendToButton.setGeometry(QRect(280, 0, 75, 23))

        self.sendToSameButton = QPushButton(self.widget_3)
        self.sendToSameButton.setObjectName(u"SendToSameButton")
        self.sendToSameButton.setGeometry(QRect(370, 0, 75, 23))
        self.sendToSameButton.hide()

        self.horizontalLayout.addWidget(self.widget_3)

        self.verticalLayout.addWidget(self.widget_2)

        self.mainContentWidget = QWidget(self.centralwidget)
        self.mainContentWidget.setObjectName(u"mainContentWidget")

        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.mainContentWidget.sizePolicy().hasHeightForWidth())

        self.mainContentWidget.setSizePolicy(sizePolicy3)
        self.mainContentWidget.setSizeIncrement(QSize(0, 0))

        self.contentLayout = QHBoxLayout(self.mainContentWidget)
        self.contentLayout.setObjectName(u"content")
        self.contentLayout.setSpacing(0)
        self.contentLayout.setContentsMargins(0,0,0,0)

        self.imageContainer = QWidget(self.mainContentWidget)

        self.scrollArea = draggableScrollArea(self.mainContentWidget)
        self.scrollArea.setObjectName(u"singleElementScrollArea")
        self.scrollArea.setWidgetResizable(True)

        self.imageLayout = QHBoxLayout(self.imageContainer)

        self.image = QLabel(self.mainContentWidget)
        self.image.setObjectName(u"image")

        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())

        self.image.setSizePolicy(sizePolicy5)
        self.image.setPixmap(QPixmap(u""))
        self.image.setScaledContents(True)

        self.scrollArea.setWidget(self.imageContainer)

        self.imageLayout.setContentsMargins(0,0,0,0)

        self.imageLayout.addWidget(self.image)
        
        self.contentLayout.setContentsMargins(0, 0, 0, 0)

        self.contentLayout.addWidget(self.scrollArea)

        self.leftButton = QPushButton(self.mainContentWidget)
        self.leftButton.setObjectName(u"leftButton")

        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.leftButton.sizePolicy().hasHeightForWidth())

        self.leftButton.setSizePolicy(sizePolicy4)
        self.leftButton.clicked.connect(self.goLeft)

        self.rightButton = QPushButton(self.mainContentWidget)
        self.rightButton.setObjectName(u"rightButton")
        sizePolicy4.setHeightForWidth(self.rightButton.sizePolicy().hasHeightForWidth())
        self.rightButton.setSizePolicy(sizePolicy4)

        self.verticalLayout.addWidget(self.mainContentWidget)

        self.rightButton.clicked.connect(self.goRight)
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomOutButton.clicked.connect(self.zoomOut)
        self.deleteButton.clicked.connect(self.deleteContent)
        self.sendToButton.clicked.connect(self.sendContentTo)
        self.sendToSameButton.clicked.connect(lambda: self.sendContentTo(sendToSameDirectory=True))

        self.retranslateUi(parent)
    # setupUi

    def retranslateUi(self, MainWindow):

        self.backButton.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.leftButton.setText(QCoreApplication.translate("MainWindow", u"<", None))
        self.image.setText("")
        self.rightButton.setText(QCoreApplication.translate("MainWindow", u">", None))
        self.zoomOutButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.zoomInButton.setText(QCoreApplication.translate("MainWindow", u"+", None))

        iconAttribute = getattr(QStyle, "SP_DialogDiscardButton")
        icon = self.style().standardIcon(iconAttribute)
        self.deleteButton.setIcon(icon)

        self.sendToButton.setText(QCoreApplication.translate("MainWindow", u"Send To", None))

    # retranslateUi 

    # TODO: Merge goLeft and goRight functions into one
    def goLeft(self):
        self.contentAmount = len(self.imageArray)

        if self.imageIndex > 0:
            self.imageIndex -=1
        else:
            self.imageIndex = self.contentAmount - 1

        if self.imageArrayPath == "Today's Picks":
            newImage = self.imageArray[self.imageIndex]
        else:
            newImage = f"{self.imageArrayPath}/{self.imageArray[self.imageIndex]}"
        
        try:
            self.setContent(newImage)
        except ZeroDivisionError as e:
            self.goLeft()
    
    def goRight(self, deletion=False):
        self.contentAmount = len(self.imageArray)
        if self.contentAmount <= 0:
            return
        if not deletion:
            if self.imageIndex < self.contentAmount - 1:
                self.imageIndex +=1
            else:
                self.imageIndex = 0

        if self.imageArrayPath == "Today's Picks":
            newImage = self.imageArray[self.imageIndex]
        else:
            try:
                newImage = f"{self.imageArrayPath}/{self.imageArray[self.imageIndex]}"
            except IndexError as e:
                self.imageIndex = 0
                newImage = f"{self.imageArrayPath}/{self.imageArray[self.imageIndex]}"

        try:
            self.setContent(newImage)
        except ZeroDivisionError as e:
            self.goRight(deletion=False)   
    
    def goBack(self, outOfContent: bool = False):
        print("Going back!")
        for widgetIndex in range(self.imageLayout.count()):
            widgetToRemove = self.imageLayout.itemAt(widgetIndex).widget()
            widgetToRemove.clear()
            self.imageLayout.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)

        nextUi = self.parentWidget().parentWidget().ui.centralwidget
        parent = self.parentWidget()
        mainUi = parent.parentWidget()

        parent.setCurrentWidget(nextUi)
        mainUi.resizeOverride()
        print(f"Todays picks: {mainUi.todaysPicks}")
        if self.updateParent == True:
            self.parentWidget().parentWidget().setDirectory("faq", directory=self.imageArrayPath)
    
    def setContent(self, contentPath: str):
        # TODO: Make functions for each content type
        # TODO: Catch broken files/nonloadable filetypes

        self.loaded = False
        print(f"Content names: {self.imageArray}")
        globalStatusBar: QStatusBar = self.parent().parent().ui.statusbar
        globalStatusBar.showMessage(f"{contentPath} - {self.imageIndex + 1}/{len(self.imageArray)}")

        if "Content to be filtered" not in contentPath:
            self.deleteButton.hide()
            self.sendToButton.hide()

        for widgetIndex in range(self.imageLayout.count()):
            widgetToRemove = self.imageLayout.itemAt(widgetIndex).widget()
            self.imageLayout.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)

        containerHeight = self.scrollArea.height()
        containerWidth = self.scrollArea.width()
        containerSize = self.scrollArea.size()

        if contentPath.endswith(imageExtensions):
            print(f"This media is an image {contentPath}")
            pixmap = QPixmap(contentPath)
            self.image.setPixmap(pixmap)

            imageSize = pixmap.size()

            newSize = getSizeAdjustedToContainer(containerSize, imageSize)

            self.image.setFixedSize(newSize)

            self.originalContentSize = newSize

            self.imageLayout.addWidget(self.image)
        
        if contentPath.endswith(videoExtension):
            print("This is a video")
            videoWidget = VideoPlayer()

            videoWidget.setMaximumSize(self.scrollArea.width(), self.scrollArea.height())
            videoWidget.setMinimumSize(100, 100)

            sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(videoWidget.sizePolicy().hasHeightForWidth())

            videoWidget.setSizePolicy(sizePolicy)

            videoWidget.abrir(contentPath, self.scrollArea.width() - 207, self.scrollArea.height())

            self.imageLayout.addWidget(videoWidget)
        
        if contentPath.endswith(gifExtension):
            print("This media is a gif")
            gifWidget = GifPlayer()

            gifWidget.setMaximumSize(self.scrollArea.width(), self.scrollArea.height())
            gifWidget.setMinimumSize(100, 100)

            sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(gifWidget.sizePolicy().hasHeightForWidth())

            gifWidget.setSizePolicy(sizePolicy)

            gifWidget.abrir(contentPath, containerSize)

            self.imageLayout.addWidget(gifWidget)
        
        self.scale = 1
        if contentPath.endswith(imageExtensions):
            self.resizeImage()
        self.updateButtonsInUI()

        if "Content to be filtered" in contentPath and self.parentWidget().parentWidget().destination:
            self.currentDestinationFolder = os.path.split(self.parentWidget().parentWidget().destination)[-1]
            self.sendToSameButton.show()
            self.sendToSameButton.setText(QCoreApplication.translate("MainWindow", f"Send To {self.currentDestinationFolder}", None))
            self.sendToSameButton.adjustSize()

        self.loaded = True
        
    def setDirectory(self):
        homeDir = str(Path.home())
        folder = QFileDialog.getExistingDirectory(caption="Choose directory", directory=homeDir, parent=None)

        if folder:
                self.imageArrayPath = folder
                self.imageArray = os.listdir(self.imageArrayPath)
                self.imageArray.sort(key=lambda filename: os.path.getctime(os.path.join(self.imageArrayPath, filename)))
                self.imageIndex = 0
    
    def wheelEvent(self, event: QWheelEvent) -> None:

        if not self.imageArray[self.imageIndex].endswith(imageExtensions): # TODO: Implement gif and video zoom
            return

        deltaY = event.angleDelta().y()

        if(deltaY < 0):
            self.zoomOut()
        if(deltaY > 0):
            self.zoomIn()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        # TODO: Implement shortcut for send to same location and send to new location
        # TODO: Deactivate delete shortcut when not filtering(currently when not in Content to be filtered directory)

        key = event.key()
        if key == Qt.Key.Key_Left:
            self.goLeft()
        elif key == Qt.Key.Key_Right:
            self.goRight()
        elif key == Qt.Key.Key_Delete:
            self.deleteContent()
    
    def zoomIn(self):

        if not self.imageArray[self.imageIndex].endswith(imageExtensions):
            return

        self.scale *= 2

        self.resizeImage()
    
    def zoomOut(self):
        if not self.imageArray[self.imageIndex].endswith(imageExtensions):
            return

        self.scale = self.scale / 2

        self.resizeImage()
    
    def removeAutoplayingMediaFromGallery(self, filename, mediaType):
        galleryFlowLayout = self.parentWidget().parentWidget().ui.flowBoi

        for column in range(galleryFlowLayout.count()):
            columnWidget = galleryFlowLayout.itemAt(column).widget()
            for element in columnWidget.children():
                try:
                    if element.fileName == filename:
                        print("Content widget to delete found!")
                        widgetToDelete = element
                        columnWidget.layout().removeWidget(widgetToDelete)
                        if mediaType == "gif":
                            widgetToDelete.gif.stop()
                            widgetToDelete.gif = None
                            widgetToDelete.buffer = None
                            widgetToDelete.label.setMovie(QMovie())
                        widgetToDelete.playlists.clear()
                        widgetToDelete.deleteLater()
                except Exception as e:
                    print("Layout hit!")
    
    def getCurrentContentPathInfo(self):

        currentImagePath = os.path.join(Path(self.imageArrayPath), self.imageArray[self.imageIndex])
        filename = self.imageArray[self.imageIndex]
        
        return { "FullPath": currentImagePath, "Filename": filename} # TODO: Make model

    def deleteContent(self):
        # TODO: Feels like this function could be merged with sendContentTo. Brainstorm that.
        try:
            print("Deletion initiatied")

            contentPathInfo = self.getCurrentContentPathInfo()

            filenameToDelete = contentPathInfo["Filename"]
            currentImagePath = contentPathInfo["FullPath"]
            self.imageArray.pop(self.imageIndex)

            widgetToRemove = self.imageLayout.itemAt(0).widget()
            widgetToRemove.clear()

            self.goRight(deletion=True)

            if currentImagePath.endswith(videoExtension):
                self.removeAutoplayingMediaFromGallery(filenameToDelete, "video")
            if currentImagePath.endswith(gifExtension):
                self.removeAutoplayingMediaFromGallery(filenameToDelete, "gif")
            
            send2trash(currentImagePath)
            self.imageArray = os.listdir(self.imageArrayPath)
            self.imageArray.sort(key=lambda filename: os.path.getctime(os.path.join(self.imageArrayPath, filename)))
            self.updateParent = True

            if len(self.imageArray) <= 0:
                self.goBack(True)
        except IndexError:
            return

    def sendContentTo(self, sendToSameDirectory=False):

        print("Sending content")
        homeDir = str(Path.home())

        contentPathInfo = self.getCurrentContentPathInfo()

        filename = contentPathInfo["Filename"]
        currentContentPath = contentPathInfo["FullPath"]

        print(f"Destination: {self.parentWidget().parentWidget().destination}")

        if not sendToSameDirectory or not self.parentWidget().parentWidget().destination:
            # TODO: Remember previous folder location and open filedialog one or two directories up
            self.parentWidget().parentWidget().destination = QFileDialog.getExistingDirectory(caption="Choose destination", directory=homeDir, parent=None)
            if not self.parentWidget().parentWidget().destination:
                print("Sending procedure cancelled")
                return
        
        if self.parentWidget().parentWidget().destination:
            self.currentDestinationFolder = os.path.split(self.parentWidget().parentWidget().destination)[-1]
            self.sendToSameButton.show()
            self.sendToSameButton.setText(QCoreApplication.translate("MainWindow", f"Send To {self.currentDestinationFolder}", None))
            self.sendToSameButton.adjustSize()

        destinationContentPath = f"{self.parentWidget().parentWidget().destination}/{filename}"

        self.imageArray.pop(self.imageIndex)

        widgetToRemove = self.imageLayout.itemAt(0).widget()
        widgetToRemove.clear()

        self.goRight(deletion=True)
        if currentContentPath.endswith(videoExtension):
            self.removeAutoplayingMediaFromGallery(filename, "video")
        if currentContentPath.endswith(gifExtension):
            self.removeAutoplayingMediaFromGallery(filename, "gif")

        print(f"Copying {currentContentPath}")
        print(f"To {destinationContentPath}")

        shutil.move(currentContentPath, destinationContentPath)

        self.parentWidget().parentWidget().todaysPicks.append(destinationContentPath)

        self.imageArray = os.listdir(self.imageArrayPath)
        self.imageArray.sort(key=lambda filename: os.path.getctime(os.path.join(self.imageArrayPath, filename)))
        self.updateParent = True

        if len(self.imageArray) <= 0:
            self.goBack(True)

    
    def resizeImage(self):
        size = self.originalContentSize

        newSize = QSize(size.width() * self.scale, size.height() * self.scale)

        self.image.setFixedSize(newSize)
    
    def resizeEvent(self, a0: QResizeEvent) -> None:
        # TODO: Move logic for each content type to it's own function
        super().resizeEvent(a0)
        self.updateButtonsInUI()

        if self.loaded:
            currentContent = f"{self.imageArrayPath}/{self.imageArray[self.imageIndex]}"
            containerSize = self.scrollArea.size()

            if currentContent.endswith(imageExtensions):
                imageSize = self.image.pixmap().size()
                newSize = getSizeAdjustedToContainer(containerSize, imageSize)
                self.originalContentSize = newSize
                self.image.setFixedSize(newSize)
                self.scale = 1
                self.resizeImage()

            elif currentContent.endswith(gifExtension):

                gifWidget = self.imageLayout.itemAt(0).widget()
                gifWidget.setMaximumSize(self.scrollArea.width(), self.scrollArea.height())
                gifWidget.setMinimumSize(100, 100)
                gifWidget.abrir(currentContent, containerSize)

            elif currentContent.endswith(videoExtension):
                videoWidget = self.imageLayout.itemAt(0).widget()
                videoWidget.setMaximumSize(self.scrollArea.width(), self.scrollArea.height())
                videoWidget.setMinimumSize(100, 100)

                videoWidget.abrir(currentContent, self.scrollArea.width() - 207, self.scrollArea.height())

    
    def updateButtonsInUI(self):
            rightButtonPosition = self.scrollArea.geometry().topRight() - QPoint(self.rightButton.width() - 1, 0)
            self.rightButton.move(rightButtonPosition)

            containerHeight = self.scrollArea.height()
            self.rightButton.setFixedHeight(containerHeight)
            leftButtonPosition = self.scrollArea.geometry().topLeft()
            self.leftButton.move(leftButtonPosition)
            self.leftButton.setFixedHeight(containerHeight)


