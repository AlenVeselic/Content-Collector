
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class removeContentTagDialog(QDialog):
    def __init__(self, listOfTags, parent=None):
        super(removeContentTagDialog, self).__init__(parent)

        self.tags = listOfTags
        self.tagNames = []

        for tag in self.tags:
            self.tagNames.append(tag[1])

        QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog)
        self.setupUi(self)

    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.horizontalLayoutWidget = QWidget(Dialog)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(20, 90, 361, 73))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.selectTagToDeleteCombobox = QComboBox(self.horizontalLayoutWidget)
        self.selectTagToDeleteCombobox.setObjectName(u"selectTagToDeleteCombobox")
        self.selectTagToDeleteCombobox.addItems(self.tagNames)

        self.horizontalLayout.addWidget(self.selectTagToDeleteCombobox)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(26, 30, 351, 20))

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Name", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"New content tag", None))
    # retranslateUi
        
    def getTagToDeleteID(self):

        for tag in self.tags:
            if self.selectTagToDeleteCombobox.currentText() == tag[1]:
                return tag[0]
