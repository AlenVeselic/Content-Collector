from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui

from views.scraper.service.scraperThread import scraperThread

class scraperView(QtWidgets.QWidget):
    destination = ""
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.horizontalLayoutMain = QtWidgets.QHBoxLayout(self)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("scraperTab")
        self.centralwidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())

        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")

        sizePolicy1 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMargin(0)

        self.verticalLayout.addWidget(self.label)

        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"scraperStateText")
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.textEdit)

        self.mediaProgressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.mediaProgressBar.setObjectName(u"mediaProgressBar")
        self.mediaProgressBar.setValue(0)

        self.verticalLayout.addWidget(self.mediaProgressBar)

        self.overallProgressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.overallProgressBar.setObjectName(u"overallProgressBar")
        self.overallProgressBar.setValue(0)

        self.verticalLayout.addWidget(self.overallProgressBar)

        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        sizePolicy2 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy2)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setSizeIncrement(QtCore.QSize(0, 0))
        self.widget.setLayoutDirection(QtCore.Qt.LeftToRight)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0,0,0,0)

        self.textEdit_2 = QtWidgets.QTextEdit(self.widget)
        self.textEdit_2.setObjectName(u"scraperDirectory")
        self.textEdit_2.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        sizePolicy3 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Ignored)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.textEdit_2.sizePolicy().hasHeightForWidth())
        self.textEdit_2.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.textEdit_2)

        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.clicked.connect(self.getDestination)

        self.horizontalLayout_3.addWidget(self.pushButton_2)

        self.verticalLayout.addWidget(self.widget)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.clicked.connect(self.runScraper)
        

        self.verticalLayout.addWidget(self.pushButton)


        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayoutMain.addWidget(self.centralwidget)
        self.retranslateUi(parent)
        
    def update(self, value):
        self.textEdit.append(value)

    def getDestination(self):
        homeDir = str(Path.home())
        folder = QtWidgets.QFileDialog.getExistingDirectory(self.pushButton, "Choose directory", homeDir)

        if folder:
                self.destination = folder
                self.textEdit_2.setText(folder)

    def runScraper(self):
        self.scraper = scraperThread(self.destination)
        self.scraper.text.connect(self.message)
        self.scraper.clear.connect(self.clearText)
        self.scraper.mediaProgress.connect(self.updateMediaProgress)
        self.scraper.overallProgress.connect(self.updateOverallProgress)
        self.scraper.start()
        
    def message(self, s):
        self.textEdit.append(s)
    def clearText(self):
        self.textEdit.setText("")
    
    def updateMediaProgress(self, newValue):
        self.mediaProgressBar.setValue(newValue)
    def updateOverallProgress(self, newValue):
        self.overallProgressBar.setValue(newValue)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", u"   Script output", None))
        self.pushButton_2.setText(_translate("MainWindow", u"Destination", None))
        self.pushButton.setText(_translate("MainWindow", u"Execute", None))
