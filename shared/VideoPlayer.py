from PyQt5 import QtMultimedia, QtMultimediaWidgets

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class VideoPlayer(QWidget):

    def __init__(self, parent=None, allowOpenVideo: bool = False):
        super(VideoPlayer, self).__init__(parent)

        self.mediaPlayer = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        btnSize = QSize(16, 16)
        self.videoWidget = QtMultimediaWidgets.QVideoWidget()

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        
        self.setSizePolicy(sizePolicy)

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        self.videoWidget.setMaximumSize(self.width(), self.height())
        self.videoWidget.setMinimumSize(100, 100)

        self.videoWidget.setSizePolicy(sizePolicy)

        self.videoContainerLayout = QHBoxLayout()

        self.videoContainer = QWidget(self)
        self.videoContainer.setObjectName("singleElementVideoContainer")
        self.videoContainer.setSizePolicy(sizePolicy)
        self.videoLayout = QVBoxLayout()
        self.videoLayout.addWidget(self.videoWidget)
        self.videoContainer.setLayout(self.videoLayout)

        self.videoContainerLayout.addWidget(self.videoContainer)

        openButton = QPushButton("Open Video")   
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setFont(QFont("Noto Sans", 8))
        openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))
        openButton.clicked.connect(self.abrir)
        if not allowOpenVideo:
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

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(100, 0, 100, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addLayout(self.videoContainerLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")


    def abrir(self, fileName, containerWidth, containerHeight):
        if fileName == '':
            fileName, _ = QFileDialog.getOpenFileName(self, "Selecciona los mediose",
                    ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if fileName != '':
            print(fileName)
            self.mediaPlayer.setMedia(
                    QtMultimedia.QMediaContent(QUrl.fromLocalFile(fileName)))
            if fileName.endswith(".gif"):
                print("Setting faster playback")
                self.mediaPlayer.setPlaybackRate(2)
                print("Speed: " + str(self.mediaPlayer.playbackRate()))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(fileName)

            self.play()

            self.videoLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.videoWidget.setFixedSize(containerWidth, containerHeight)

    def clear(self):
        self.gif = None
        self.mediaPlayer = None

    def play(self):
        if self.mediaPlayer.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())
