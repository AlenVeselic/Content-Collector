
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from shared.getSizeAdjustedToContainer import getSizeAdjustedToContainer

# TODO: Make parent class for this and VideoPlayer

class GifPlayer(QWidget):
    def __init__(self, parent=None, allowOpenGif: bool = False):
        super(GifPlayer, self).__init__(parent)

        self.consolePrefix = "[ Gif player ]"

        self.mediaPlayer = QLabel()
        btnSize = QSize(16, 16)

        self.gif = QMovie()

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        
        self.setSizePolicy(sizePolicy)

        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        self.mediaPlayer.setSizePolicy(sizePolicy)

        self.gifContainerLayout = QHBoxLayout()

        self.gifContainer = QWidget(self)
        self.gifContainer.setObjectName("singleElementGifContainer")
        self.gifContainer.setSizePolicy(sizePolicy)
        self.gifLayout = QVBoxLayout()
        self.gifLayout.addWidget(self.mediaPlayer)
        self.gifContainer.setLayout(self.gifLayout)

        self.gifContainerLayout.addWidget(self.gifContainer)

        openButton = QPushButton("Open Video")   
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setFont(QFont("Noto Sans", 8))
        openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))
        openButton.clicked.connect(self.abrir)
        if not allowOpenGif:
            openButton.hide()

        self.playButton = QPushButton()
        self.playButton.setProperty("cssClass", "playButton")
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(100, 0, 100, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addLayout(self.gifContainerLayout)
        layout.addLayout(controlLayout)

        self.setLayout(layout)

        self.gif.error.connect(self.handleError)


    def abrir(self, fileName, containerSize):
        if fileName == '':
            fileName, _ = QFileDialog.getOpenFileName(self, "Selecciona los mediose",
                    ".", "Gif Files (*.gif)")

        if fileName != '':
            print(fileName)
            self.gif = QMovie(fileName)
            self.mediaPlayer.setMovie(
                    self.gif)
            self.durationChanged()
            self.playButton.setEnabled(True)
            self.gif.stateChanged.connect(self.mediaStateChanged)
            self.gif.frameChanged.connect(self.positionChanged)

            self.gif.setBackgroundColor(QColor(QColorConstants.Black))
            
            self.gif.start()

            gifSize = self.gif.frameRect()

            newSize = getSizeAdjustedToContainer(containerSize - QSize(0, 66), gifSize)

            self.gif.setScaledSize(newSize) 

            self.gifLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            gifContainerSize = self.gifContainer.size()

            print(f"{self.consolePrefix} Container size: {gifContainerSize}")
    
    def clear(self):
        self.gif = QMovie()
        self.mediaPlayer.setMovie(self.gif)

    def play(self):
        print(self.gif.state())
        if self.gif.state() == QMovie.MovieState.Running:
            self.gif.setPaused(True)
        else:
            self.gif.setPaused(False)

    def mediaStateChanged(self, state):
        print(self.consolePrefix + str(self.gif.state()))
        if self.gif.state() == QMovie.MovieState.Running:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self):
        print(self.gif.frameCount())
        self.positionSlider.setRange(0, self.gif.frameCount())

    def setPosition(self, position):
        print(position)
        self.gif.jumpToFrame(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.gif.lastErrorString())
