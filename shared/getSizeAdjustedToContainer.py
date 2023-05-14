from PyQt5.QtCore import *

# TODO: Move into functions

def getSizeAdjustedToContainer(containerSize, contentSize):

    if contentSize.width() > containerSize.width():
        print("This image's width is greater than the imagecontainer. ")
    if contentSize.height() > containerSize.height():
        print("This image's height is greater than the imagecontainer.")
    
    if contentSize.height() > contentSize.width():
        imageRatio = (contentSize.width()/contentSize.height())
        print("Height is greater")
        newHeight = containerSize.height()
        newWidth = containerSize.height() * imageRatio
    elif contentSize.height() == contentSize.width():
        imageRatio = (contentSize.width()/contentSize.height())
        if containerSize.height() > containerSize.width() or containerSize.height() == containerSize.width():
            newHeight = containerSize.width()
            newWidth = containerSize.width()
        else:
            newHeight = containerSize.height()
            newWidth = containerSize.height()

    else:
        print("Width is greater")
        imageRatio = (contentSize.width()/contentSize.height()) #(contentSize.height()/contentSize.width())
        newHeight = containerSize.height() 
        newWidth = containerSize.height() * imageRatio
        if newHeight > containerSize.height():
            heightDifference = newHeight - containerSize.height()
            newHeight -= heightDifference
            newWidth -= heightDifference
        if newWidth > containerSize.width():
            newWidth = newWidth/2
            newHeight = newHeight/2

            
        
    print("Size format: (widthxheight)")
    print("Image size: " + str(contentSize.width()) + "x" + str(contentSize.height()))
    print("Container size: " + str(containerSize.width()) + "x" + str(containerSize.height()))
    print("ImageRatio: " + str(imageRatio))
    imageRatio = (contentSize.width()/contentSize.height())
    print("New image size: " + str(newWidth) + "x" + str(newHeight))

    return QSize(newWidth, newHeight)