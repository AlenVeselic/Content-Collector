
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class contentTagDialog(QDialog):
    def __init__(self, parent=None):
        super(contentTagDialog, self).__init__(parent)

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

        self.textEdit = QTextEdit(self.horizontalLayoutWidget)
        self.textEdit.setObjectName(u"textEdit")

        self.horizontalLayout.addWidget(self.textEdit)

        self.typeLabel = QLabel(self.horizontalLayoutWidget)
        self.typeLabel.setObjectName(u"typeLabel")

        self.horizontalLayout.addWidget(self.typeLabel)

        self.typeTextEdit = QTextEdit(self.horizontalLayoutWidget)
        self.typeTextEdit.setObjectName(u"typeTextEdit")

        self.horizontalLayout.addWidget(self.typeTextEdit)

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
        self.typeLabel.setText(QCoreApplication.translate("Dialog", u"Type: ", None))
    # retranslateUi
        
    def getTagData(self):
        return {"name": self.textEdit.toPlainText(),
                "type": self.typeTextEdit.toPlainText()}
