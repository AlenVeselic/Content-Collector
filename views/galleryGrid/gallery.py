
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from pathlib import Path

from views.scraper.scraperView import scraperView
from views.settings.settingsView import settingsView
from views.galleryGrid.FlowLayout import FlowLayout
from views.galleryGrid.tabWidgetWithResizableTabBars import tabWidgetWithResizableTabBar

# TODO: Rename class
# TODO: Move other files in this directory to their own folder, so that it is known which file holds the view

class galleryView(QMainWindow):
    setDirectory = ""

    stylePath = Path(Path.cwd(),'default.qss')
    def setupUi(self, MainWindow, returning):
        self.playlists = []
        self.videoplayers = []
        self.vidNumber = 0
        self.numberOfColumns = 6
        self.maxColumnWidth = 100
        self.finalColumnMargin = 65
        self.currentPage = 1
        self.availablePages = 1

        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(979, 713)

        MainWindow.setAutoFillBackground(False)

        self.actionSet_Directory = QAction(MainWindow)
        self.actionSet_Directory.setObjectName(u"actionSet_Directory")

        self.actionTodays_Picks = QAction(MainWindow)
        self.actionTodays_Picks.setObjectName(u"actionTodays_Picks")

        self.baseWindow = QStackedWidget(MainWindow)
        self.baseWindow.setEnabled(True)

        self.centralwidget = QWidget()
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.baseWindow.sizePolicy().hasHeightForWidth())

        self.baseWindow.setSizePolicy(sizePolicy)

        self.baseWindow.setLayoutDirection(Qt.LeftToRight)

        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.gallery_tab = QWidget()
        self.gallery_tab.setObjectName(u"gallery_tab")

        self.horizontalLayout = QVBoxLayout(self.gallery_tab)
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.galleryBar = QHBoxLayout()
        self.nextPageButton = QPushButton()
        self.pagesLabel = QLabel()
        self.pagesLabel.setAlignment(Qt.AlignCenter)
        self.previousPageButton = QPushButton()

        self.galleryBar.addWidget(self.previousPageButton)
        self.galleryBar.addWidget(self.pagesLabel)
        self.galleryBar.addWidget(self.nextPageButton)

        self.horizontalLayout.addLayout(self.galleryBar)

        self.scrollArea = QScrollArea(self.gallery_tab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 935, 608))

        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())

        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy1)
        self.scrollAreaWidgetContents.setAutoFillBackground(True)

        self.horizontalLayout_2 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.baseWindow.setMinimumWidth(100)

        self.flowBoi = FlowLayout()

        self.horizontalLayout.addWidget(self.scrollArea)

        self.scraper_tab = QWidget()
        self.scraper_tab.setObjectName(u"scraper_tab")

        self.scraperLayout = QHBoxLayout(self.scraper_tab)
        self.scraperLayout.setObjectName(u"scraperLayout")

        self.scraperView = scraperView(self.scraper_tab)
        self.scraperView.setObjectName(u"scraperView")

        self.scraperLayout.addWidget(self.scraperView)

        self.settings_tab = QWidget()
        self.settings_tab.setObjectName(u"settings_tab")

        self.settingsLayout = QHBoxLayout(self.settings_tab)
        self.settingsLayout.setObjectName(u"settingsLayout")

        self.settingsView = settingsView(self.settings_tab)
        self.settingsView.setObjectName(u"settingsView")
        self.settingsLayout.addWidget(self.settingsView)

        self.tabViews = [
            {
                "name": "Gallery",
                "widget": self.gallery_tab
            },
            {
                "name": "Scraper",
                "widget": self.scraper_tab
            },
            {
                "name": "Settings",
                "widget": self.settings_tab
            }
        ]

        self.tabWidgetWithResizableTabBars = tabWidgetWithResizableTabBar(self.tabViews, self.centralwidget, self.stylePath)

        self.verticalLayout_2.addWidget(self.tabWidgetWithResizableTabBars)

        MainWindow.setCentralWidget(self.baseWindow)
        self.baseWindow.addWidget(self.centralwidget)

        self.baseWindow.setContentsMargins(0,0,0,0)
        self.centralwidget.setContentsMargins(0,0,0,0)
        self.verticalLayout_2.setContentsMargins(0,0,0,0)
        self.verticalLayout_2.setSpacing(0)

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 979, 21))

        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")

        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionSet_Directory)
        self.menuFile.addAction(self.actionTodays_Picks)

        self.actionSet_Directory.triggered.connect(self.setDirectory)
        self.actionTodays_Picks.triggered.connect(lambda: self.setDirectory("act", contentFilenames=MainWindow.todaysPicks))

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi
        
    def updatePages(self, text):
        self.pagesLabel.setText(text)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSet_Directory.setText(QCoreApplication.translate("MainWindow", u"Set Directory", None))
        self.actionTodays_Picks.setText(QCoreApplication.translate("MainWindow", u"Check Today's Picks", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))

        self.nextPageButton.setText(QCoreApplication.translate("MainWindow", u">", None))
        self.previousPageButton.setText(QCoreApplication.translate("MainWindow", u"<", None))
        self.pagesLabel.setText(QCoreApplication.translate("MainWindow", f"{self.currentPage} / {self.availablePages}", None))
    # retranslateUi
