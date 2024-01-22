from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class createContentInDatabaseDialog(QDialog):
    def __init__(self, filename, tags, parent=None):
        super(createContentInDatabaseDialog, self).__init__(parent)

        self.filename = filename
        self.tags = tags
        self.currentInputVerticalPosition = 0

        QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog)
        self.setupUi(self)

    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(600, 800)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 750, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayoutWidget = QWidget(Dialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(20, 90, 600, 800))

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        

        # Table: Content
        # original_directory - string - should be set once file leaves filtration - currently set manually

        self.originalDirectoryInput = self.createSelectDirectoryInputComponent(self.verticalLayoutWidget, self.getOriginalDirectory, "originalDirectory", "Select original directory")
        self.originalDirectoryInput.textChanged.connect(self.updateCurrentLocation)

        # original_filename - string

        self.originalFilenameInput = self.createTextInputComponent(self.verticalLayoutWidget, "originalFilename", "Filename: ", self.filename)
        self.originalFilenameInput.textChanged.connect(self.updateCurrentLocation)

        # original_title - string - set from updated scraper

        self.originalTitleInput = self.createTextInputComponent(self.verticalLayoutWidget, "originalTitle", "Title: ")

        # currentLocation - string - should be set whenever the file is moved after it has initially been filtered 
        # - is combination of domain/directory and filename, this points to the current most relevant file for this content entry

        self.currentLocationInput = self.createSelectDirectoryInputComponent(self.verticalLayoutWidget, self.getCurrentLocation, "currentLocation", "Select current location")

        # source - string enum

        self.sourceInput = self.createTextInputComponent(self.verticalLayoutWidget, "source", "Source: ")

        # scraped_on - timestamp - should be generated if the entry is made from scraper, otherwise take date from file

        self.scrapedOnInput = self.createCalendarInputComponent(self.verticalLayoutWidget, "scrapedOn", "Scraped on: ")

        # created_on - entry creation date - generated

        self.createdOnInput = self.createCalendarInputComponent(self.verticalLayoutWidget, "createdOn", "Created on: ")

        # Table: tags_content
        # tags - multiselect

        tagsForInput = []

        print(self.tags)

        for tag in self.tags:
             tagsForInput.append(tag[2])
        
        self.tagInput = self.createListInputComponent(self.verticalLayoutWidget, "contentTags", "Choose the tags related to this content ", tagsForInput)

        self.formTitle = QLabel(Dialog)
        self.formTitle.setObjectName(u"formTitle")
        self.formTitle.setGeometry(QRect(26, 30, 351, 20))

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        self.buttonBox.setGeometry(QRect(30, self.currentInputVerticalPosition , 341, 32))

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        # self.nameInputLabel.setText(QCoreApplication.translate("Dialog", u"Name", None))
        self.formTitle.setText(QCoreApplication.translate("Dialog", u"New content creation", None))
    # retranslateUi
        
    def getOriginalDirectory(self):
        homeDir = str(Path.home())
        folder = QFileDialog.getExistingDirectory(self.verticalLayoutWidget, "Choose directory", homeDir)

        if folder:
                self.originalDirectoryInput.setText(folder)
    
    def getCurrentLocation(self):
        print("Getting current location")
        homeDir = str(Path.home())
        dialog = QFileDialog(self)

        if dialog.exec_():
                self.currentLocationInput.setText(dialog.selectedFiles()[0])
                
    def updateCurrentLocation(self):
        self.currentLocationInput.setText(f"{self.originalDirectoryInput.toPlainText()}/{self.originalFilenameInput.toPlainText()}")

    def getContentData(self):

        selectedTags = []
        for item in self.tagInput.selectedItems():
             selectedTags.append(item.text())

        return {"original_directory": self.originalDirectoryInput.toPlainText(),
                "original_filename": self.originalFilenameInput.toPlainText(),
                "original_title": self.originalTitleInput.toPlainText(),
                "current_location": self.currentLocationInput.toPlainText(),
                "source": self.sourceInput.toPlainText(),
                "scraped_on": self.scrapedOnInput.selectedDate(),
                "created_on": self.createdOnInput.selectedDate(),
                "content_tags": selectedTags
                }
    
    def createSelectDirectoryInputComponent(self, parent, buttonCallback, componentName, buttonLabel):

        print("Creating new directory component")

        wrapperWidget = QWidget(parent)
        wrapperWidget.setObjectName(f"{componentName}LayoutWidget")
        wrapperWidget.setGeometry(QRect(20, self.currentInputVerticalPosition, 600, 30))

        layout = QHBoxLayout(wrapperWidget)
        layout.setObjectName(f"{componentName}Layout")
        layout.setContentsMargins(0, 0, 100, 0)

        input = QTextEdit(wrapperWidget)
        input.setObjectName(f"{componentName}")

        selectDirectoryButton = QPushButton(wrapperWidget)
        selectDirectoryButton.setObjectName(f"{componentName}SelectButton")
        selectDirectoryButton.clicked.connect(buttonCallback)
        selectDirectoryButton.setText(QCoreApplication.translate("MainWindow", f"{buttonLabel}", None))

        layout.addWidget(selectDirectoryButton)

        layout.addWidget(input)

        self.currentInputVerticalPosition += 40

        return input
    
    def createTextInputComponent(self, parent, componentName, componentLabel, defaultValue=""):

        print("Creating new text input component")

        wrapperWidget = QWidget(parent)
        wrapperWidget.setObjectName(f"{componentName}LayoutWidget")
        wrapperWidget.setGeometry(QRect(20, self.currentInputVerticalPosition, 600, 30))

        layout = QHBoxLayout(wrapperWidget)
        layout.setObjectName(f"{componentName}Layout")
        layout.setContentsMargins(0, 0, 100, 0)

        label = QLabel(wrapperWidget)
        label.setObjectName(f"{componentName}Label")
        label.setText(f"{componentLabel}")

        layout.addWidget(label)

        input = QTextEdit(wrapperWidget)
        input.setObjectName(f"{componentName}")
        input.setPlainText(defaultValue)

        layout.addWidget(input)

        self.currentInputVerticalPosition += 40

        return input
    
    def createCalendarInputComponent(self, parent, componentName, componentLabel):

        print("Creating new directory component")

        wrapperWidget = QWidget(parent)
        wrapperWidget.setObjectName(f"{componentName}LayoutWidget")
        wrapperWidget.setGeometry(QRect(20, self.currentInputVerticalPosition, 600, 200))

        layout = QHBoxLayout(wrapperWidget)
        layout.setObjectName(f"{componentName}Layout")
        layout.setContentsMargins(0, 0, 100, 0)

        label = QLabel(wrapperWidget)
        label.setObjectName(f"{componentName}Label")
        label.setText(f"{componentLabel}")

        layout.addWidget(label)

        input = QCalendarWidget(wrapperWidget)
        input.setObjectName(f"{componentName}")
        #input.setContentsMargins(0,0,0,300)

        layout.addWidget(input)

        self.currentInputVerticalPosition += 225

        return input
    
    def createListInputComponent(self, parent, componentName, componentLabel, items):

        print("Creating new list component")

        wrapperWidget = QWidget(parent)
        wrapperWidget.setObjectName(f"{componentName}LayoutWidget")
        wrapperWidget.setGeometry(QRect(20, self.currentInputVerticalPosition, 600, 400))

        layout = QVBoxLayout(wrapperWidget)
        layout.setObjectName(f"{componentName}Layout")
        layout.setContentsMargins(0, 0, 100, 0)

        label = QLabel(wrapperWidget)
        label.setObjectName(f"{componentName}Label")
        label.setText(f"{componentLabel}")

        layout.addWidget(label)

        input = QListWidget(wrapperWidget)
        input.setObjectName(f"{componentName}")
        input.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        input.addItems(items)
        #input.setContentsMargins(0,0,0,300)

        layout.addWidget(input)

        self.currentInputVerticalPosition += 225

        return input

         
