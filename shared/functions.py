from PyQt5 import QtWidgets, QtMultimediaWidgets
from PyQt5.QtCore import *
from shared.ClickableLabel import ClickableLabel

def calculateElementHeight(width, element):
    consoleName = "[ Element height calculation ] "
    if isinstance(element, ClickableLabel):
        if element.pixmap():

            elementRatio = (element.pixmap().height()/element.pixmap().width())
        if element.movie():
            elementRatio = (element.movie().frameRect().height()/element.movie().frameRect().width())
        
    elif isinstance(element, QtMultimediaWidgets.QVideoWidget):
        print(consoleName + "SizeHint? " +  str(element.sizeHint()))
        if not (element.sizeHint() == QSize(-1, -1) or element.sizeHint() == QSize(0, 0) or element.sizeHint() == QSize()):
            elementRatio = (element.sizeHint().height()/element.sizeHint().width())
        else:
            print(consoleName + "Using regular size for video")
            elementRatio = (element.size().width()/element.size().height())
    elif isinstance(element, QtWidgets.QLabel):
        elementRatio = (element.movie().frameRect().height()/element.movie().frameRect().width())
    else:
        print(consoleName + "Unkown element type - making square")
        return width
    
    print(f"{consoleName} Element ratio: {elementRatio}")

    return width*elementRatio