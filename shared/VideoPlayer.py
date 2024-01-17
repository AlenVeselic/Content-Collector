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

        self.muteButton = QPushButton()
        self.muteButton.setEnabled(True)
        self.muteButton.setFixedHeight(24)
        self.muteButton.setIconSize(btnSize)
        self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.muteButton.clicked.connect(self.toggleMute)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.positionLabel = QLabel()
        self.positionLabel.setFixedHeight(24)
        self.positionLabel.setObjectName("positionLabel")
        self.positionLabel.setText("0:00 / 0:00")

        self.positionBarLayout = QHBoxLayout()
        self.positionBarLayout.setContentsMargins(100, 0, 100, 0)

        self.positionBarLayout.addWidget(self.positionSlider)
        self.positionBarLayout.addWidget(self.positionLabel)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.sliderMoved.connect(self.setVolume)
        self.volumeSlider.setFixedWidth(100)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(100, 0, 100, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.muteButton)
        controlLayout.addWidget(self.volumeSlider)

        self.controlsLayout = QVBoxLayout()
        self.controlsLayout.setContentsMargins(100, 0, 100, 0)
        self.controlsLayout.addLayout(self.positionBarLayout)
        self.controlsLayout.addLayout(controlLayout)
        

        layout = QVBoxLayout()
        layout.addLayout(self.videoContainerLayout)
        layout.addLayout(self.controlsLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.volumeChanged.connect(self.volumeChanged)
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
            self.videoWidget.setFixedSize(containerWidth, containerHeight - 150)

    def clear(self):
        self.gif = None
        self.mediaPlayer = None

    def play(self):
        if self.mediaPlayer.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
    def toggleMute(self):
        self.mediaPlayer.setMuted(not self.mediaPlayer.isMuted())
        if(self.mediaPlayer.isMuted()):
            self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        else:
            self.muteButton.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

        positionMinutes = int((position/1000)/60)
        positionSeconds = int((position/1000)%60)

        durationMinutes = int((self.mediaPlayer.duration()/1000)/60)
        durationSeconds = int((self.mediaPlayer.duration()/1000)%60)

        justifiedPositionMinutes = str(positionMinutes).rjust(2, "0")
        justifiedPositionSeconds = str(positionSeconds).rjust(2, "0")

        justifiedDurationMinutes = str(durationMinutes).rjust(2, "0")
        justifiedDurationSeconds = str(durationSeconds).rjust(2, "0")

        self.positionLabel.setText(f"{justifiedPositionMinutes}:{justifiedPositionSeconds} / {justifiedDurationMinutes}:{justifiedDurationSeconds}")

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        self.volumeSlider.setValue(self.mediaPlayer.volume())
    
    def volumeChanged(self, volume):
        self.volumeSlider.setValue(volume)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def setVolume(self, position):
        self.mediaPlayer.setVolume(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())
