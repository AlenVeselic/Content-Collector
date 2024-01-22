from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os, logging, shelve, fileinput, psycopg2
from cryptography.fernet import Fernet
from shared.database import getDatabaseOptions

from views.settings.contentTagDialog import contentTagDialog
from views.settings.removeContentTagDialog import removeContentTagDialog

# TODO: When removing a list item, generate dropdown menu to pick what you are deleting. Current implementation is very rough, having to input text
# for the tag you want to delete.
# OR
# Give user the ability to select list items and click the remove button. This would prompt a dialog window listing what they
# are about to delete. Yes deletes listed items, No doesn't.

class settingsView(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.newConfig = {}
        self.oldConfig = {}
        self.shelvePath = r'./Data/CollectorData'
        self.shelveSettings = {}
        self.decryptKey = ""

        self.horizontalLayoutMain = QHBoxLayout(self)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName(u"settingsTab")

        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.settingsScrollArea = QScrollArea(self.centralwidget)
        self.settingsScrollArea.setObjectName(u"settingsScrollArea")
        self.settingsScrollArea.setWidgetResizable(True)

        self.settingsScrollAreaWidgetContents = QWidget()
        self.settingsScrollAreaWidgetContents.setObjectName(u"settingsScrollAreaWidgetContents")
        self.settingsScrollAreaWidgetContents.setGeometry(QRect(0, 0, 829, 622))

        self.verticalLayout_6 = QVBoxLayout(self.settingsScrollAreaWidgetContents)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.booruSettingsLabel = QLabel(self.settingsScrollAreaWidgetContents)
        self.booruSettingsLabel.setObjectName(u"booruSettingsLabel")

        self.verticalLayout_6.addWidget(self.booruSettingsLabel)

        self.booruScraperSettingsWrapper = QWidget(self.settingsScrollAreaWidgetContents)
        self.booruScraperSettingsWrapper.setObjectName(u"booruScraperSettingsWrapper")
        self.booruScraperSettingsWrapper.setContentsMargins(0,0,0,0)
        self.verticalLayout_2 = QVBoxLayout(self.booruScraperSettingsWrapper)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.booruCheckBoxSettings = QWidget(self.booruScraperSettingsWrapper)
        self.booruCheckBoxSettings.setObjectName(u"booruCheckBoxSettings")

        self.horizontalLayout_5 = QHBoxLayout(self.booruCheckBoxSettings)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")

        self.useApiCheckBox = QCheckBox(self.booruCheckBoxSettings)
        self.useApiCheckBox.setObjectName(u"useApiCheckBox")

        self.horizontalLayout_5.addWidget(self.useApiCheckBox)

        self.skipBooruCheckBox = QCheckBox(self.booruCheckBoxSettings)
        self.skipBooruCheckBox.setObjectName(u"skipBooruCheckBox")

        self.horizontalLayout_5.addWidget(self.skipBooruCheckBox)


        self.verticalLayout_2.addWidget(self.booruCheckBoxSettings)

        self.destinationFolderHeader = QWidget(self.booruScraperSettingsWrapper)
        self.destinationFolderHeader.setObjectName(u"destinationFolderHeader")

        self.horizontalLayout = QHBoxLayout(self.destinationFolderHeader)
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.destinationFoldersLabel = QLabel(self.destinationFolderHeader)
        self.destinationFoldersLabel.setObjectName(u"destinationFoldersLabel")

        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.destinationFoldersLabel.sizePolicy().hasHeightForWidth())

        self.destinationFoldersLabel.setSizePolicy(sizePolicy)
        self.destinationFoldersLabel.setSizeIncrement(QSize(0, 0))

        self.horizontalLayout.addWidget(self.destinationFoldersLabel)

        self.destinationFolderAdd = QPushButton(self.destinationFolderHeader)
        self.destinationFolderAdd.setObjectName(u"destinationFolderAdd")

        self.horizontalLayout.addWidget(self.destinationFolderAdd)

        self.destinationFolderRemove = QPushButton(self.destinationFolderHeader)
        self.destinationFolderRemove.setObjectName(u"destinationFolderRemove")

        self.horizontalLayout.addWidget(self.destinationFolderRemove)
        self.horizontalLayout.setContentsMargins(0,0,0,0)


        self.verticalLayout_2.addWidget(self.destinationFolderHeader)

        self.destinationFoldersList = QListWidget(self.booruScraperSettingsWrapper)
        self.destinationFoldersList.setObjectName(u"destinationFoldersList")

        self.verticalLayout_2.addWidget(self.destinationFoldersList)

        self.tagsHeader = QWidget(self.booruScraperSettingsWrapper)
        self.tagsHeader.setObjectName(u"tagsHeader")
        self.horizontalLayout_4 = QHBoxLayout(self.tagsHeader)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0,0,0,0)
        self.tagsLabel = QLabel(self.tagsHeader)
        self.tagsLabel.setObjectName(u"tagsLabel")
        sizePolicy.setHeightForWidth(self.tagsLabel.sizePolicy().hasHeightForWidth())
        self.tagsLabel.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.tagsLabel)

        self.tagAdd = QPushButton(self.tagsHeader)
        self.tagAdd.setObjectName(u"tagAdd")

        self.horizontalLayout_4.addWidget(self.tagAdd)

        self.tagRemove = QPushButton(self.tagsHeader)
        self.tagRemove.setObjectName(u"tagRemove")

        self.horizontalLayout_4.addWidget(self.tagRemove)


        self.verticalLayout_2.addWidget(self.tagsHeader)

        self.tagsList = QListWidget(self.booruScraperSettingsWrapper)
        self.tagsList.setObjectName(u"tagsList")

        self.verticalLayout_2.addWidget(self.tagsList, 5)

        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0,0,0,0)

        self.verticalLayout_6.addWidget(self.booruScraperSettingsWrapper)

        self.redditSettingsLabel = QLabel(self.settingsScrollAreaWidgetContents)
        self.redditSettingsLabel.setObjectName(u"redditSettingsLabel")

        self.verticalLayout_6.addWidget(self.redditSettingsLabel)

        self.redditSettingsWrapper = QWidget(self.settingsScrollAreaWidgetContents)
        self.redditSettingsWrapper.setObjectName(u"redditSettingsWrapper")

        self.horizontalLayout_2 = QHBoxLayout(self.redditSettingsWrapper)

        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.redditUserSettings = QWidget(self.redditSettingsWrapper)
        self.redditUserSettings.setObjectName(u"redditUserSettings")

        self.verticalLayout_3 = QVBoxLayout(self.redditUserSettings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")

        self.skipRedditCheckBox = QCheckBox(self.redditUserSettings)
        self.skipRedditCheckBox.setObjectName(u"skipRedditCheckBox")

        self.verticalLayout_3.addWidget(self.skipRedditCheckBox)

        self.redditUsernameLabel = QLabel(self.redditUserSettings)
        self.redditUsernameLabel.setObjectName(u"redditUsernameLabel")

        self.verticalLayout_3.addWidget(self.redditUsernameLabel)

        self.usernameInput = QLineEdit(self.redditUserSettings)
        self.usernameInput.setObjectName(u"usernameInput")

        self.verticalLayout_3.addWidget(self.usernameInput)

        self.passwordLabel = QLabel(self.redditUserSettings)
        self.passwordLabel.setObjectName(u"passwordLabel")

        self.verticalLayout_3.addWidget(self.passwordLabel)

        self.passwordInput = QLineEdit(self.redditUserSettings)
        self.passwordInput.setObjectName(u"passwordInput")
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout_3.addWidget(self.passwordInput)

        self.appIDLabel = QLabel(self.redditUserSettings)
        self.appIDLabel.setObjectName(u"appIDLabel")

        self.verticalLayout_3.addWidget(self.appIDLabel)

        self.appIDInput = QLineEdit(self.redditUserSettings)
        self.appIDInput.setObjectName(u"appIDInput")

        self.verticalLayout_3.addWidget(self.appIDInput)

        self.appSecretLabel = QLabel(self.redditUserSettings)
        self.appSecretLabel.setObjectName(u"appSecretLabel")

        self.verticalLayout_3.addWidget(self.appSecretLabel)

        self.appSecretInput = QLineEdit(self.redditUserSettings)
        self.appSecretInput.setObjectName(u"appSecretInput")
        self.appSecretInput.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout_3.addWidget(self.appSecretInput)

        self.customFeedNameLabel = QLabel(self.redditUserSettings)
        self.customFeedNameLabel.setObjectName(u"customFeedNameLabel")

        self.verticalLayout_3.addWidget(self.customFeedNameLabel)

        self.customFeedNameInput = QLineEdit(self.redditUserSettings)
        self.customFeedNameInput.setObjectName(u"customFeedNameInput")

        self.verticalLayout_3.addWidget(self.customFeedNameInput)

        self.horizontalLayout_2.addWidget(self.redditUserSettings)

        self.specificSourceSettings = QWidget(self.redditSettingsWrapper)
        self.specificSourceSettings.setObjectName(u"specificSourceSettings")
        self.verticalLayout_4 = QVBoxLayout(self.specificSourceSettings)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.enableSpecificSourceDownload = QCheckBox(self.specificSourceSettings)
        self.enableSpecificSourceDownload.setObjectName(u"enableSpecificSourceDownload")

        self.verticalLayout_4.addWidget(self.enableSpecificSourceDownload)

        self.specificSourceScrollArea = QScrollArea(self.specificSourceSettings)
        self.specificSourceScrollArea.setObjectName(u"specificSourceScrollArea")
        self.specificSourceScrollArea.setWidgetResizable(True)
        self.specificSourceScrollAreaContents = QWidget()
        self.specificSourceScrollAreaContents.setObjectName(u"specificSourceScrollAreaContents")
        self.specificSourceScrollAreaContents.setGeometry(QRect(0, 0, 373, 194))
        self.verticalLayout_5 = QVBoxLayout(self.specificSourceScrollAreaContents)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.possibleSourcesLabel = QLabel(self.specificSourceScrollAreaContents)
        self.possibleSourcesLabel.setObjectName(u"possibleSourcesLabel")

        self.verticalLayout_5.addWidget(self.possibleSourcesLabel)

        self.possibleSourcesList = QListWidget(self.specificSourceScrollAreaContents)
        self.possibleSourcesList.setObjectName(u"possibleSourcesList")
        self.possibleSourcesList.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        self.verticalLayout_5.addWidget(self.possibleSourcesList)

        self.specificSourceScrollArea.setWidget(self.specificSourceScrollAreaContents)

        self.verticalLayout_4.addWidget(self.specificSourceScrollArea)


        self.horizontalLayout_2.addWidget(self.specificSourceSettings)

        self.contentTagsWrapper = QWidget(self.settingsScrollAreaWidgetContents)
        self.contentTagsWrapper.setObjectName(u"contentTagsContents")
        self.contentTagsWrapper.setGeometry(QRect(0, 0, 373, 194))

        self.contentTagsLayout = QVBoxLayout(self.contentTagsWrapper)
        self.contentTagsLayout.setObjectName(u"contentTagsLayout")

        self.contentTagsHeader = QWidget(self.contentTagsWrapper)

        self.contentTagsHeaderLayout = QHBoxLayout(self.contentTagsHeader)

        self.contentTagsLabel = QLabel(self.contentTagsHeader)
        self.contentTagsLabel.setObjectName(u"contentTagsLabel")
        self.contentTagsLabel.setSizePolicy(sizePolicy)
        self.contentTagsLabel.setSizeIncrement(QSize(0, 0))

        self.contentTagsHeaderLayout.addWidget(self.contentTagsLabel)

        self.contentTagsAdd = QPushButton(self.contentTagsHeader)
        self.contentTagsAdd.setObjectName(u"contentTagsAdd")

        self.contentTagsHeaderLayout.addWidget(self.contentTagsAdd)

        self.contentTagsRemove = QPushButton(self.contentTagsHeader)
        self.contentTagsRemove.setObjectName(u"contentTagsRemove")

        self.contentTagsHeaderLayout.addWidget(self.contentTagsRemove)
        self.contentTagsHeaderLayout.setContentsMargins(0,0,0,0)

        self.contentTagsLayout.addWidget(self.contentTagsHeader)

        self.contentTagsList = QListWidget(self.contentTagsWrapper)
        self.contentTagsList.setObjectName(u"contentTagsList")

        self.contentTagsLayout.addWidget(self.contentTagsList)

        self.verticalLayout_6.addWidget(self.redditSettingsWrapper)

        self.verticalLayout_6.addWidget(self.contentTagsWrapper)

        self.settingsScrollArea.setWidget(self.settingsScrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.settingsScrollArea)

        self.actionButtons = QWidget(self.centralwidget)
        self.actionButtons.setObjectName(u"actionButtons")
        self.horizontalLayout_3 = QHBoxLayout(self.actionButtons)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.revertButton = QPushButton(self.actionButtons)
        self.revertButton.setObjectName(u"revertButton")

        self.horizontalLayout_3.addWidget(self.revertButton)

        self.saveButton = QPushButton(self.actionButtons)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout_3.addWidget(self.saveButton)

        self.verticalLayout.addWidget(self.actionButtons)

        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayoutMain.addWidget(self.centralwidget)

        self.useApiCheckBox.stateChanged.connect(self.setUseApi)
        self.skipBooruCheckBox.stateChanged.connect(self.setSkipBooru)

        self.tagAdd.clicked.connect(self.addTag)
        self.tagRemove.clicked.connect(self.removeTag)

        self.destinationFolderAdd.clicked.connect(self.addDestination)
        self.destinationFolderRemove.clicked.connect(self.removeDestination)

        self.contentTagsAdd.clicked.connect(self.addContentTag)
        self.contentTagsRemove.clicked.connect(self.removeContentTag)

        self.skipRedditCheckBox.stateChanged.connect(self.setSkipReddit)

        self.saveButton.clicked.connect(self.saveSettings)

        self.retranslateUi(parent)

    def retranslateUi(self, MainWindow):
        self.booruSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Booru Scraper Settings", None))
        self.useApiCheckBox.setText(QCoreApplication.translate("MainWindow", u"Use api", None))
        self.skipBooruCheckBox.setText(QCoreApplication.translate("MainWindow", u"Skip booru scraping", None))

        self.destinationFoldersLabel.setText(QCoreApplication.translate("MainWindow", u"Destination Folders (For duplicate checking while scraping)", None))
        self.destinationFolderAdd.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.destinationFolderRemove.setText(QCoreApplication.translate("MainWindow", u"Remove", None))

        self.tagsLabel.setText(QCoreApplication.translate("MainWindow", u"Tags", None))
        self.tagAdd.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.tagRemove.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.redditSettingsLabel.setText(QCoreApplication.translate("MainWindow", u"Reddit Scraper Settings", None))
        self.skipRedditCheckBox.setText(QCoreApplication.translate("MainWindow", u"Skip Reddit scraping", None))
        self.redditUsernameLabel.setText(QCoreApplication.translate("MainWindow", u"Username", None))
        self.passwordLabel.setText(QCoreApplication.translate("MainWindow", u"Password", None))
        self.appIDLabel.setText(QCoreApplication.translate("MainWindow", u"App Id", None))
        self.appSecretLabel.setText(QCoreApplication.translate("MainWindow", u"App Secret", None))
        self.customFeedNameLabel.setText(QCoreApplication.translate("MainWindow", u"Custom Feed Name", None))
        self.enableSpecificSourceDownload.setText(QCoreApplication.translate("MainWindow", u"Download only from specific sources", None))
        self.possibleSourcesLabel.setText(QCoreApplication.translate("MainWindow", u"Possible sources", None))

        self.contentTagsLabel.setText(QCoreApplication.translate("MainWindow", u"Content Tags", None))
        self.contentTagsAdd.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.contentTagsRemove.setText(QCoreApplication.translate("MainWindow", u"Remove", None))

        self.revertButton.setText(QCoreApplication.translate("MainWindow", u"Revert", None))
        self.saveButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
    # retranslateUi

    def setUseApi(self):
        self.newConfig["BOORU_USE_API"] = str(self.useApiCheckBox.isChecked())
    
    def setSkipBooru(self):
        self.newConfig["SKIP_BOORU"] = str(self.skipBooruCheckBox.isChecked())
    
    def setSkipReddit(self):
        self.newConfig["SKIP_REDDIT"] = str(self.skipRedditCheckBox.isChecked())
    
    def getDecryptKey(self):
        decryptKey = os.environ.get("REDDIT_SENSITIVE_DATA_SECRET")

        if decryptKey:
            decryptKeyInBytes = bytes(decryptKey, 'utf-8')
            self.decryptKey = Fernet(decryptKeyInBytes)
        else:
            print("Generating new decrypt key")
            decryptKey = Fernet.generate_key()
            for line in fileinput.input(".env", inplace = 1):
                print(line.replace("REDDIT_SENSITIVE_DATA_SECRET=",f'REDDIT_SENSITIVE_DATA_SECRET={str(decryptKey)[1:]}').rstrip())
            fileinput.close()
            os.environ["REDDIT_SENSITIVE_DATA_SECRET"] = str(decryptKey)[1:]
            print("New decrypt key generated and added to environment file")


    def setRedditCredentials(self):

        username = self.usernameInput.text()
        password = self.passwordInput.text()
        appID = self.appIDInput.text()
        appSecret = self.appSecretInput.text()

        if username != self.oldConfig["REDDIT_USERNAME"]:
            self.newConfig["REDDIT_USERNAME"] = username
        
        if password != self.oldConfig["REDDIT_PASSWORD"]:
            passwordInBytes = bytes(password, 'utf-8')
            self.newConfig["REDDIT_PASSWORD"] = self.decryptKey.encrypt(passwordInBytes)

        if appID != self.oldConfig["REDDIT_APP_USERNAME"]:
            self.newConfig["REDDIT_APP_USERNAME"] = appID

        if appSecret != self.oldConfig["REDDIT_APP_PASSWORD"]:
            appSecretInBytes = bytes(appSecret, 'utf-8')
            self.newConfig["REDDIT_APP_PASSWORD"] = self.decryptKey.encrypt(appSecretInBytes)
    
    def setRedditCustomFeed(self):
        customFeed = self.customFeedNameInput.text()

        if customFeed != self.oldConfig["REDDIT_CUSTOM_FEED_NAME"]:
            self.newConfig["REDDIT_CUSTOM_FEED_NAME"] = customFeed


    def addTag(self):
        text, ok = QInputDialog().getText(self, "QInputDialog().getText()",
                                     "New tag name:", QLineEdit.Normal)
        if ok and text:
            self.tagsList.addItem(text)

    def removeTag(self):
        text, ok = QInputDialog().getText(self, "QInputDialog().getText()",
                                     "Tag to remove:", QLineEdit.Normal)
        if ok and text:
            tagToRemove = self.tagsList.findItems(text)

            if tagToRemove:
                self.tagsList.removeItemWidget(tagToRemove[0])
    
    def addDestination(self):
        text = QFileDialog.getExistingDirectory(self, "Choose directory")

        if text:
            self.destinationFoldersList.addItem(text)

    def removeDestination(self):
        text, ok = QInputDialog().getText(self, "QInputDialog().getText()",
                                     "Destination to remove:", QLineEdit.Normal)
        if ok and text:
            destinationToRemove = self.destinationFoldersList.findItems(text)

            if destinationToRemove:
                self.destinationFoldersList.removeItemWidget(destinationToRemove[0])

    def addContentTag(self):
        print("ADDING CONTENT TAG")

        createTagDialog = contentTagDialog()
        if createTagDialog.exec_() == QDialog.Accepted:

            databaseOptions = getDatabaseOptions()
            
            newTagData = createTagDialog.getTagData()
            print(newTagData)

            databaseConnection = psycopg2.connect(**databaseOptions)
            databaseConnection.autocommit = True

            databaseCursor = databaseConnection.cursor()

            insertTagQuery = "INSERT INTO tags (name, type) VALUES (%s, %s)"

            databaseCursor.execute(insertTagQuery, (newTagData["name"], newTagData["type"],))
            
            databaseCursor.close()
            databaseConnection.close()



    def removeContentTag(self):
        print("REMOVING CONTENT TAG")

        removeTagDialog = removeContentTagDialog(self.contentTags)
        if removeTagDialog.exec_() == QDialog.Accepted:

            databaseOptions = getDatabaseOptions()
            
            tagID = removeTagDialog.getTagToDeleteID()
            print(tagID)

            databaseConnection = psycopg2.connect(**databaseOptions)
            databaseConnection.autocommit = True

            databaseCursor = databaseConnection.cursor()

            deleteTagQuery = "DELETE FROM tags WHERE id = %s"

            databaseCursor.execute(deleteTagQuery, (tagID,))
            
            databaseCursor.close()
            databaseConnection.close()
    
    def loadContentTags(self):
        print("Getting content tags from database")

        
        databaseOptions = getDatabaseOptions()

        databaseConnection = psycopg2.connect(**databaseOptions)
        databaseCursor = databaseConnection.cursor()

        getTagsQuery = '''SELECT * FROM tags''' 

        databaseCursor.execute(getTagsQuery)

        tags = databaseCursor.fetchall()

        self.contentTags = tags
        print(self.contentTags)

        databaseCursor.close()
        databaseConnection.close()
    
    def saveSettings(self):
        self.setRedditCredentials()
        self.setRedditCustomFeed()

        for configKey in self.newConfig:
            logging.info(f"{configKey}: {self.newConfig[configKey]}")
            os.environ[configKey] = str(self.newConfig[configKey])

        tagItems = [self.tagsList.item(index).text() for index in range(self.tagsList.count())]
        destinationDirectoryItems = [self.destinationFoldersList.item(index).text() for index in range(self.destinationFoldersList.count())]

        tags = []
        for item in tagItems:
            tags.append(item)

        destinationDirectories = []
        for item in destinationDirectoryItems:
            destinationDirectories.append(item)

        shelveSettings = shelve.open(self.shelvePath)

        shelveSettings["terms"] = tags
        shelveSettings["destinationDirectories"] = destinationDirectories
        if "settings" not in shelveSettings.keys():
            shelveSettings["settings"] = {}
        
        shelveSettings["settings"] = self.newConfig

        shelveSettings.close()
    
    def loadShelveSettings(self, shelve: shelve.Shelf):

        try:
            self.shelveSettings = shelve["settings"]
        except KeyError as e:
            self.shelveSettings = {}


    def getBoolSetting(self, key: str):
        if key in self.shelveSettings.keys():
            self.oldConfig[key] = self.shelveSettings[key] == "True"
            os.environ[key] = self.shelveSettings[key]
        else:
            self.oldConfig[key] = os.environ.get(key) == "True"
    
    def getTextSetting(self, key:str, sensitive: bool = False):
        if key in self.shelveSettings.keys():
            if sensitive and self.decryptKey != "":
                encryptedValueInBytes = self.shelveSettings[key]
                self.oldConfig[key] = self.decryptKey.decrypt(encryptedValueInBytes).decode('utf-8')
            else:  
                self.oldConfig[key] = self.shelveSettings[key]
        else:
            self.oldConfig[key] = os.environ.get(key)

    def refresh(self):
        logging.info("Getting current settings")

        self.tagsList.clear()
        self.destinationFoldersList.clear()
        self.possibleSourcesList.clear()

        os.makedirs("Data", exist_ok=True)

        self.getDecryptKey()

        data = shelve.open(self.shelvePath)

        self.loadShelveSettings(data)

        try:
            shelveTags = data["terms"]
        except KeyError as e:
            shelveTags = []
        
        try:
            shelveDirectories = data["destinationDir"]
        except KeyError as e:
            shelveDirectories = []
        
        try:
            shelveFolders = data["destinationDirectories"]
        except KeyError as e:
            shelveFolders = []

        for tag in shelveTags:
            self.tagsList.addItem(tag)

        for folder in shelveFolders:
            self.destinationFoldersList.addItem(f"{folder}")
        
        self.getBoolSetting("BOORU_USE_API")
        self.useApiCheckBox.setChecked(self.oldConfig["BOORU_USE_API"])

        self.getBoolSetting("SKIP_BOORU")
        self.skipBooruCheckBox.setChecked(self.oldConfig["SKIP_BOORU"])

        self.getBoolSetting("SKIP_REDDIT")
        self.skipRedditCheckBox.setChecked(self.oldConfig["SKIP_REDDIT"])
        
        self.getTextSetting("REDDIT_USERNAME")
        self.usernameInput.setText(self.oldConfig["REDDIT_USERNAME"])

        self.getTextSetting("REDDIT_PASSWORD", True)
        self.passwordInput.setText(self.oldConfig["REDDIT_PASSWORD"])

        self.getTextSetting("REDDIT_APP_USERNAME")
        self.appIDInput.setText(self.oldConfig["REDDIT_APP_USERNAME"])

        self.getTextSetting("REDDIT_APP_PASSWORD", True)
        self.appSecretInput.setText(self.oldConfig["REDDIT_APP_PASSWORD"])

        self.getTextSetting("REDDIT_CUSTOM_FEED_NAME")
        self.customFeedNameInput.setText(self.oldConfig["REDDIT_CUSTOM_FEED_NAME"])

        self.getBoolSetting("REDDIT_DOWNLOAD_ONLY_CONTENT_FROM_SPECIFIC_SITE")
        self.enableSpecificSourceDownload.setChecked(self.oldConfig["REDDIT_DOWNLOAD_ONLY_CONTENT_FROM_SPECIFIC_SITE"])

        self.oldConfig["REDDIT_SPECIFIC_SITE"] = os.environ.get("REDDIT_SPECIFIC_SITE").split(',')
        
        try:
            shelveRedditSources = data["redditSources"]
        except KeyError as e:
            shelveRedditSources = []

        for possibleSource in shelveRedditSources:
            self.possibleSourcesList.addItem(possibleSource)

        if self.oldConfig["REDDIT_DOWNLOAD_ONLY_CONTENT_FROM_SPECIFIC_SITE"]:
            for site in self.oldConfig["REDDIT_SPECIFIC_SITE"]:
                foundItem = self.possibleSourcesList.findItems(site, Qt.MatchFlag.MatchExactly)
                if foundItem:
                    foundItem[0].setSelected(True)
        else:
            self.possibleSourcesList.setDisabled(True)

        self.loadContentTags()

        self.contentTagsList.clear()

        for tag in self.contentTags:
            self.contentTagsList.addItem(tag[2])

        logging.info("Settings refreshed")
        