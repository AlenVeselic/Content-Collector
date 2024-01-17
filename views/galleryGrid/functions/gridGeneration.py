import os
from PyQt5 import QtGui, QtWidgets, QtMultimedia, QtCore

from shared.ClickableLabel import ClickableLabel
from shared.ClickableVideoWidget import ClickableVideoWidget

from shared.functions import calculateElementHeight
from constants.mediaExtensions import gifExtension, videoExtension

from views.galleryGrid.FlowLayout import FlowLayout
from views.galleryGrid.functions.columnWidget import ColumnWidget
from views.galleryGrid.functions.GridWidget import GridWidget

# TODO: This file has had a lot of changes and is mid refactor. Check which functions are even still used in the application.

def generateImageWidgetThreaded(arrayPath, path, file, mainWindow, app, pixmap: QtGui.QPixmap, label: ClickableLabel, imageSignal):

    label.setElement(arrayPath, path, file)
    label.setScaledContents(True)
    label.mainWindow = app

    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())

    label.setSizePolicy(sizePolicy)

    label.imagePath = path
    label.setPixmap(pixmap)
    imageSignal.emit(label)

def generateGifWidgetThreaded(arrayPath, path, file, app, label: ClickableLabel, labelSetSignal):
    label.setElement(arrayPath, path, file)

    label.mainWindow = app

    label.setMinimumSize(100, 100)

    labelSetSignal.emit(label)

def generateVideoWidgetThreaded(arrayPath, path, file, counter, appVideoplayers, appPlaylists, appWindow, app, videoWidget: ClickableVideoWidget, widgetSetSignal):
    videoWidget.set(arrayPath, path, file)

    videoWidget.mainWindow = app

    videoWidget.setMinimumSize(100,100)

    widgetSetSignal.emit(videoWidget)

    

def generateImageWidget(arrayPath, path, file, mainWindow, app, pixmap: QtGui.QPixmap, label: ClickableLabel):

    pixmap.load(path)

    label.setElement(arrayPath, path, file)
    label.setScaledContents(True)
    label.mainWindow = app

    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())

    label.setSizePolicy(sizePolicy)
    label.setMinimumSize(100, 100)

    pixmapRect = pixmap.rect()

    elementRatio = pixmapRect.height()/pixmapRect.width()

    label.setMaximumHeight(int((mainWindow.centralwidget.height()/6.5)*elementRatio))
    label.imagePath = path
    label.setPixmap(pixmap)

def generateVideoWidget(arrayPath, path, file, counter, appVideoplayers, appPlaylists, appWindow):
    videoWidget = ClickableVideoWidget(arrayPath, path, file)
    videoWidget.setMinimumSize(100,100)

    videoPlayer = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    appVideoplayers.append(videoPlayer)
    video = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(path))

    playlist = QtMultimedia.QMediaPlaylist()
    appPlaylists.append(playlist)
    appPlaylists[counter].addMedia(video)
    appPlaylists[counter].setPlaybackMode(QtMultimedia.QMediaPlaylist.Loop)
    

    appVideoplayers[counter].setPlaylist(appPlaylists[counter])
    appVideoplayers[counter].setVolume(0)
    appVideoplayers[counter].setVideoOutput(videoWidget)
    appVideoplayers[counter].play()

    elementRatio = (video.canonicalResource().resolution().height()/video.canonicalResource().resolution().width())

    videoWidget.setMaximumHeight(int(appWindow.scrollArea.width()/6.5*elementRatio))
    
    print(appVideoplayers[counter])


    videoWidget.imagePath = path

    return videoWidget

def generateGifWidget(arrayPath, path, file, appWindow):

    label = ClickableLabel()
    label.setElement(arrayPath, path, file)
    label.mainWindow = appWindow
    gif = QtGui.QMovie(path)
    
    label.setMovie(gif)
    gif.start()
    gifRatio = gif.frameRect().height()/gif.frameRect().width()
    gif.setScaledSize(QtCore.QSize(int(appWindow.centralwidget.width()/6.5), int(appWindow.centralwidget.width()/6.5)/gifRatio))

    label.setMinimumSize(100, 100)

    return label

def getChildNumberPerColumn(columns, futureNumberOfColumns):

    contentNumber = 0

    column: ColumnWidget
    for column in columns:

        contentNumber += len(column.children())
    
    return contentNumber/futureNumberOfColumns

def getContentFromColumns(columns, contentNumberPerColumn):
    extraContent = []

    column: ColumnWidget
    for column in columns:
        extraContentFromColumn = getContentFromColumn(column, contentNumberPerColumn)
        for content in extraContentFromColumn:
            extraContent.append(content)
            
    return extraContent

def getContentFromColumn(column: ColumnWidget, allowedContentNumber: int = 1):
    columnWidgets = column.children()
    extraContent = []
    while len(column.children()) > allowedContentNumber:
        currentColumnLength = len(column.children())
        if currentColumnLength == 1:
            print("No more content to move")
            break
        freshExtraContent = column.children().pop()
        column.layout().removeWidget(freshExtraContent)
        freshExtraContent.setParent(None)
        extraContent.append(freshExtraContent)
    return extraContent

def getContentFromColumnWithMax(column: ColumnWidget, max: int = 1, rowIndex: int = -1):
    columnWidgets = column.children()
    if rowIndex + 1 >= len(column.children()):
        print("Rowindex out of range")
        return []
    


    extraContent = []
    while len(extraContent) < max:
        currentColumnLength = len(column.children())
        if currentColumnLength == 1:
            print("No more content to move")
            break
        freshExtraContent = column.children().pop(rowIndex)
        print(f"Moving target {freshExtraContent.fileName}")
        alreadyMoved.append(freshExtraContent.fileName)

        extraContent.append(freshExtraContent)
    return extraContent
    

def emptyColumns(columns):

    extraContent = []

    column: ColumnWidget
    for column in columns:
        columnWidgets = column.children()
        while len(column.children()) > 1:
            currentColumnLength = len(column.children())
            freshExtraContent = column.children().pop()
            column.layout().removeWidget(freshExtraContent)
            freshExtraContent.setParent(None)
            extraContent.append(freshExtraContent)
    return extraContent




def moveContent(source: FlowLayout, difference, mode):
    print("Move content")
    columns: list[ColumnWidget] = []
    oldColumnNumber = source.count()

    maxRows = 0
    
    for columnNumber in range(source.count()):
        columns.append(source.itemAt(columnNumber).widget())
        currentColumnChildrenNumber = source.itemAt(columnNumber).widget().children()
        if len(currentColumnChildrenNumber) < maxRows or maxRows == 0:
            maxRows = len(currentColumnChildrenNumber)
    
    if mode == "expand":
        newColumnNumber = source.count() + difference
        newColumns = []
        for columnNumber in range(difference):
            newColumnWidget = ColumnWidget()
            newColumnWidget.setObjectName("column")
            newColumnWidget.setLayout(QtWidgets.QVBoxLayout())
            newColumnWidget.setMinimumWidth(100)
            newColumns.append(newColumnWidget)
        
        for column in newColumns:
            source.addWidget(column)
        
        columns: list[ColumnWidget] = []

        for columnNumber in range(source.count()):
            columns.append(source.itemAt(columnNumber).widget())

        filenames = []
        
        for column in range(source.count()):
            print(f"Column: {column} Item count: {len(source.itemAt(column).widget().children())}")

            for element in source.itemAt(column).widget().children():
                try:
                    print(f"Directory: {element.contentDirectory}")
                    contentDirectory = element.contentDirectory
                    print(f"File: {element.fileName}")
                    if os.path.exists(os.path.join(contentDirectory, element.fileName)):
                        filenames.append(element.fileName)
                    else:
                        element.deleteLater()
                    

                except Exception as e:
                    print(f"Layout hit")
        
        expectedGrid = []
        filenames.sort(key=lambda filename: os.path.getctime(os.path.join(contentDirectory, filename)))
        for column in range(newColumnNumber):
            expectedGrid.append([])

        columnNumber = 0
        for filename in filenames:
                expectedGrid[columnNumber].append(filename)
                columnNumber += 1
                if columnNumber >= newColumnNumber:
                    columnNumber = 0

        content = emptyColumns(columns)

        for columnIndex, column in enumerate(expectedGrid):
            for rowIndex, fileName in enumerate(column):
                for contenItem in content:
                    if contenItem.fileName == fileName:
                        expectedContent = contenItem
                        break
                columns[columnIndex].layout().addWidget(contenItem)

        for column in range(source.count()):
            print(f"Column: {column} Item count: {len(source.itemAt(column).widget().children())}")
            for element in source.itemAt(column).widget().children():
                try:
                    print(f"File: {element.fileName}")
                except Exception as e:
                    print(f"Layout hit")


        print("Expanding into")
    elif mode == "shrink":
        newColumnNumber = source.count() - difference
        print("Shrinking out of " + str(oldColumnNumber) + " to " + str(newColumnNumber) + " columns")

        columnsToEmpty = []
        for columnNumber in range(difference):
            currentColumnToEmptyIndex = oldColumnNumber-columnNumber-1
            columnsToEmpty.append(source.itemAt(currentColumnToEmptyIndex).widget())
        
        filenames = []
        
        for column in range(source.count()):
            print(f"Column: {column} Item count: {len(source.itemAt(column).widget().children())}")
            for element in source.itemAt(column).widget().children():
                try:
                    print(f"File: {element.fileName}")
                    contentDirectory = element.contentDirectory
                    if os.path.exists(os.path.join(contentDirectory, element.fileName)):
                        filenames.append(element.fileName)
                    else:
                        element.deleteLater()
                except Exception as e:
                    print(f"Layout hit")
        
        expectedGrid = []
        filenames.sort(key=lambda filename: os.path.getctime(os.path.join(contentDirectory, filename)))
        for column in range(newColumnNumber):
            expectedGrid.append([])

        columnNumber = 0
        for filename in filenames:
                expectedGrid[columnNumber].append(filename)
                columnNumber += 1
                if columnNumber >= newColumnNumber:
                    columnNumber = 0

        content = emptyColumns(columns)
        
        for columnIndex, column in enumerate(expectedGrid):
            for rowIndex, fileName in enumerate(column):
                for contenItem in content:
                    if contenItem.fileName == fileName:
                        expectedContent = contenItem
                        break
                columns[columnIndex].layout().addWidget(contenItem)
        
        column: ColumnWidget
        for column in columnsToEmpty:
            source.removeWidget(column)
            column.setParent(None)

    else: 
        print("Unknown mode")

def moveContentFromTo(source: FlowLayout, columnFrom: int, columnTo: int, contentAmount: int):
    print(f"Moving from {columnFrom} to {columnTo}")
    tallColumn: ColumnWidget = source.itemAt(columnFrom).widget()
    shortColumn: ColumnWidget = source.itemAt(columnTo).widget()
    newTallColumnNumber = len(tallColumn.children()) - contentAmount
    contentForShortColumn = getContentFromColumn(tallColumn, newTallColumnNumber)

    for content in contentForShortColumn:
        shortColumn.layout().addWidget(content)

def moveContentFromToWithRowIndex(source: FlowLayout, columnFrom: int, columnTo: int, contentAmount: int, rowFromIndex: int = -1, rowToIndex:int = -1):
    print(f"Moving from {columnFrom}:{rowFromIndex} to {columnTo}:{rowToIndex}")
    try:
        columnFrom: ColumnWidget = source.itemAt(columnFrom).widget()
        columnTo: ColumnWidget = source.itemAt(columnTo).widget()
    except Exception as e:
        print(e)
        if e.__str__() == "'NoneType' object has no attribute 'widget'":
            return
        
    contentForShortColumn = getContentFromColumnWithMax(columnFrom, contentAmount, rowFromIndex)

    for content in contentForShortColumn:
        columnTo.layout().insertWidget(rowToIndex, content)

def setGridColumnSettings(gridWidth):
    numberOfColumns = 6
    finalItemMargin = 60
    if gridWidth > 1000:
        numberOfColumns = 8 
        finalItemMargin = 57
    
    maxWidth = gridWidth/numberOfColumns
    return {"numberOfColumns": numberOfColumns, "maxWidth" : maxWidth, "finalItemMargin": finalItemMargin}

def resizeGrid(mainWindow):
    currentScrollArea: QtWidgets.QScrollArea = mainWindow.ui.scrollArea
    currentFlowLayout: FlowLayout = mainWindow.ui.flowBoi
    gridWidget: QtWidgets.QWidget = mainWindow.ui.gallery_tab

    gridSettings = setGridColumnSettings(gridWidget.width())
    numberOfColumns = gridSettings["numberOfColumns"]
    maxWidth = gridSettings["maxWidth"]
    finalItemMargin = gridSettings["finalItemMargin"]

    sizeMatrix = []
    sizeRow = []
    columnRows = []
    columnHeights = []
    lineWidth = 0

    columnDifference = mainWindow.ui.numberOfColumns - numberOfColumns

    mainWindow.ui.numberOfColumns = numberOfColumns
    mainWindow.ui.maxColumnWidth = maxWidth
    mainWindow.ui.finalColumnMargin = finalItemMargin

    columnWidgets = []

    absoluteColumnDifference = abs(columnDifference)

    if columnDifference > 0:
        moveContent(currentFlowLayout, absoluteColumnDifference, "shrink")
    
    if columnDifference < 0:
        moveContent(currentFlowLayout, absoluteColumnDifference, "expand")

    for flowColumn in range(currentFlowLayout.count()):
        columnWidgets.append(currentFlowLayout.itemAt(flowColumn).widget())

    currentColumnNumber = 1
    rowNumber = 0

    column: ColumnWidget
    for index, column in enumerate(columnWidgets):

        
        print("Column " + str(currentColumnNumber) + " of " + str(numberOfColumns))
        currentColumnNumber += 1
        print("column minimumWidth: " + str(column.minimumWidth()))
        column.isLastInRow = False
        column.row = rowNumber

        if maxWidth > column.minimumWidth():
            basicWidth = maxWidth
        else:
            basicWidth = column.minimumWidth()  

        if lineWidth + (basicWidth*2.75) < gridWidget.width(): 
                print("resizing")
                
                column.setMaximumWidth(int(basicWidth)) 

                sizeRow.append(1)

                lineWidth += basicWidth

                columnHeights.append((column.height(), index))
        else:
            column.isLastInRow = True
            if not mainWindow.ui.scrollArea.verticalScrollBar().isVisible():
                column.setMaximumWidth(int(gridWidget.width() - lineWidth - finalItemMargin))
            else: 
                print("Test width: " + str(lineWidth + basicWidth))
                print("Area width: " + str(gridWidget.width()))
                print("Item Width: " + str(basicWidth))
                print("The difference between the end and the last element: " + str(lineWidth + basicWidth - gridWidget.width()))
                if -(lineWidth + basicWidth - gridWidget.width()) < basicWidth*1.75:
                    print("Stretch")
                    sizeRow.append(1.5)
                    sizeRow = []
                    sizeMatrix.append(sizeRow)
                    column.setMaximumWidth(int(gridWidget.width() - lineWidth - finalItemMargin))
                else: 
                    print("There is space")
                    print("The difference between the end and the last element: " + str(lineWidth + basicWidth - gridWidget.width()))
                    column.setMaximumWidth(int(basicWidth)) 
                    sizeRow.append(2)
                    sizeMatrix.append(sizeRow)
                    sizeRow = []
                lineWidth = 0
                columnHeights.append((column.height(), index))
                columnRows.append(columnHeights)
                columnHeights = []
                rowNumber += 1
        
        column.layout().setContentsMargins(0, 0, 0, 0)
        column.layout().setSpacing(0)


    if len(columnHeights) > 0:
        columnRows.append(columnHeights)
        columnHeights = []

def shuffleColumnElementsBasedOnHeight(columnRows):
    '''
        *Deprecated*
        The commented out parts are part of this functions functionality. They were commented out because although they would fix the line height of the columns,
        they ultimately messed up the order of the images on the grid creating a dissonance in order between the images in single element and gallery views.

        TODO: Create line height column shuffler that retains the correct content order
        or
        TODO: Add more stages to resizeGrid, that takes into account, when the flow layout's column would start to stack and actually deletes those columns, migrating
        the content over to the remaining columns and retaining the content order. Similar to the current functionality.
    '''
    shortestColumnHeight = 0
    shortestColumnIndex = 0
    tallestColumnHeight = 0
    tallestColumnIndex = 0
    if len(columnRows) > 1:
        for rowIndex, row in enumerate(columnRows):
            if len(row) > 1:
                for index, column in enumerate(row):
                    print(f"Column {column[1] + 1} height: {column[0]}")
                    if index == 0:
                        shortestColumnHeight = column[0]
                        tallestColumnHeight = column[0]
                    if column[0] < shortestColumnHeight:
                        shortestColumnHeight = column[0]
                        shortestColumnIndex = column[1]
                    if column[0] > tallestColumnHeight:
                        tallestColumnHeight = column[0]
                        tallestColumnIndex = column[1]
                # if (tallestColumnHeight - shortestColumnHeight) > 100:
                #     moveContentFromTo(currentFlowLayout, tallestColumnIndex, shortestColumnIndex, 1)
    if len(columnRows) == 1:
        for index, column in enumerate(columnRows[0]):
            print(f"Column {column[1] + 1} height: {column[0]}")
            if index == 0:
                shortestColumnHeight = column[0]
                tallestColumnHeight = column[0]
            if column[0] < shortestColumnHeight:
                shortestColumnHeight = column[0]
                shortestColumnIndex = column[1]
            if column[0] > tallestColumnHeight:
                tallestColumnHeight = column[0]
                tallestColumnIndex = column[1]

        # if (tallestColumnHeight - shortestColumnHeight) > 100:
        #     moveContentFromTo(currentFlowLayout, tallestColumnIndex, shortestColumnIndex, 1)





def setGridSizing(mainWindow):
    newFlow = FlowLayout()
    newWidge = QtWidgets.QWidget()
    newWidge.setStyleSheet('QWidget[class="column"]{background-color: orange; border: 2px solid black;}')
    lineWidth = 0

    print("Scrollbar visibility: " + str(mainWindow.ui.scrollArea.verticalScrollBar().isVisible()))

    currentWidth = 0
    widthIsSet = True

    if mainWindow.ui.scrollArea.width() > 1000:
        numberOfColumns = 8
        maxWidth = mainWindow.ui.scrollArea.width()/numberOfColumns

        finalItemMargin = 75
    else:
        numberOfColumns = 6
        maxWidth = mainWindow.ui.scrollArea.width()/numberOfColumns
        finalItemMargin = 65
    
    sizeMatrix = []
    sizeRow = []
    content = mainWindow.content
    stretch = False

    print("Items: " + str(len(content)))

    columns = []
    for column in range(numberOfColumns - 1):
        newColumn = QtWidgets.QVBoxLayout()
        columns.append(newColumn)

    columnNumber = 0
    counter = 0
    for item in content:
        print("Adding" + str(counter))
        if columnNumber < numberOfColumns - 2:
            columnNumber += 1
        else:
            columnNumber = 0
        counter += 1
    
    print("Items: " + str(len(content)))
    
    columnWidgets = []

    for column in columns:
        newColumnWidget = QtWidgets.QWidget()
        newColumnWidget.setProperty("class", "column")
        newColumnWidget.setLayout(column)
        newColumnWidget.setMinimumWidth(100)
        newColumnWidget.setMinimumHeight(1000)
        columnWidgets.append(newColumnWidget)

    columnGenCounter = 0

    column: QtWidgets.QWidget
    for column in columnWidgets:
        
        print("Column " + str(columnGenCounter + 1) + " of " + str(numberOfColumns))
        columnGenCounter += 1
        print("column minimumWidth: " + str(column.minimumWidth()))

        if maxWidth > column.minimumWidth():
            basicWidth = maxWidth
        else:
            basicWidth = column.minimumWidth()  

        if lineWidth + (basicWidth*2.75) < mainWindow.ui.scrollArea.width(): 
                print(str(column.maximumWidth() - mainWindow.ui.scrollArea.height()/6.5))
                if column.maximumSize() != QtCore.QSize(int(basicWidth), int(mainWindow.ui.scrollArea.height()/6.5)):
                    print("resizing")
                    if isinstance(column, ClickableLabel):
                        column.setMaximumWidth(int(basicWidth)) 
                    else:
                        column.setMaximumWidth(int(basicWidth)) 
                sizeRow.append(1)
                lineWidth += basicWidth
        else:
            if not mainWindow.ui.scrollArea.verticalScrollBar().isVisible():
                column.setMaximumWidth(int(mainWindow.ui.scrollArea.width() - lineWidth - finalItemMargin))
            else: 
                print("Test width: " + str(lineWidth + basicWidth))
                print("Area width: " + str(mainWindow.ui.scrollArea.width()))
                print("Item Width: " + str(basicWidth))
                print("The difference between the end and the last element: " + str(lineWidth + basicWidth - mainWindow.ui.scrollArea.width()))
                if -(lineWidth + basicWidth - mainWindow.ui.scrollArea.width()) < basicWidth*1.75:
                    print("Stretch")
                    sizeRow.append(1.5)
                    sizeRow = []
                    sizeMatrix.append(sizeRow)
                    column.setMaximumWidth(int(mainWindow.ui.scrollArea.width() - lineWidth - finalItemMargin))
                else: 
                    print("There is space")
                    print("The difference between the end and the last element: " + str(lineWidth + basicWidth - mainWindow.ui.scrollArea.width()))
                    column.setMaximumWidth(int(basicWidth)) 
                    sizeRow.append(2)
                    sizeMatrix.append(sizeRow)
                    sizeRow = []
                lineWidth = 0
        print("Items in column: " + str(column.layout().count()))

        print("Layout height: " + str(column.layout().sizeHint().height()))
        print("Widget height: " + str(column.height()))

        print("LineWidth: " + str(lineWidth))
        
        print("Items in column: " + str(column.layout().count()))
        print("Column margins: " + str(column.layout().setContentsMargins(0, 0, 0, 0)))
        print("Column spacing: " + str(column.layout().setSpacing(0)))
        

    columnNumber = 0
    lineWidth = basicWidth*(numberOfColumns-2)
    for elementNumber in range(len(mainWindow.content)):

        if columnNumber >= numberOfColumns - 1:
            columnNumber = 0
        else:
            print("Column: " + str(columnNumber))
        
        element = mainWindow.content[elementNumber]

        element.mainWindow = mainWindow
        
        if columnWidgets[columnNumber].width() < basicWidth:
            height = calculateElementHeight(basicWidth, element)
        else:
            height = calculateElementHeight(int(mainWindow.ui.scrollArea.width() - lineWidth - finalItemMargin), element)
        
        if isinstance(element, QtWidgets.QLabel) and element.movie() != None:
            if columnWidgets[columnNumber].width() < basicWidth:
                element.movie().setScaledSize(QtCore.QSize(basicWidth, height))
            else:
                element.movie().setScaledSize(QtCore.QSize(int(mainWindow.ui.scrollArea.width() - lineWidth - finalItemMargin), height)) 

        print("Height result: " + str(height))
        element.setMaximumHeight(height)
        
        columnWidgets[columnNumber].layout().addWidget(element)
        columnNumber += 1
    
    print(str(sizeMatrix))

    for column in columnWidgets:
            newFlow.addWidget(column)

        
    
    mainWindow.ui.flowBoi = newFlow
    newWidge.setLayout(newFlow)
    newWidge.layout()._hspacing = 0

    return newWidge

def createGrid(mainWindow):
    print("This function will initialize a gallery grid")
    newFlow = FlowLayout()
    newWidge = GridWidget(mainWindow.resizeTrigger)
    newWidge.setObjectName("gridWidget")
    lineWidth = 0

    print("Scrollbar visibility: " + str(mainWindow.ui.scrollArea.verticalScrollBar().isVisible()))

    currentWidth = 0
    widthIsSet = True

    if mainWindow.ui.scrollArea.width() > 1000:
        numberOfColumns = 8
        maxWidth = mainWindow.ui.scrollArea.width()/numberOfColumns

        finalItemMargin = 75
    else:
        numberOfColumns = 6
        maxWidth = mainWindow.ui.scrollArea.width()/numberOfColumns
        finalItemMargin = 65
    
    sizeMatrix = []
    sizeRow = []
    content = mainWindow.content
    stretch = False

    print("Items: " + str(len(content)))

    columns = []
    for column in range(numberOfColumns - 1):
        newColumn = QtWidgets.QVBoxLayout()
        columns.append(newColumn)

    columnWidgets = []
    
    for column in columns:
        newColumnWidget = ColumnWidget(mainWindow.resizeTrigger)
        newColumnWidget.setObjectName("column")
        newColumnWidget.setLayout(column)
        newColumnWidget.setMinimumWidth(100)
        columnWidgets.append(newColumnWidget)
    
    columnGenCounter = 0

    column: ColumnWidget
    for column in columnWidgets:
        
        print("Column " + str(columnGenCounter + 1) + " of " + str(numberOfColumns))
        columnGenCounter += 1
        print("column minimumWidth: " + str(column.minimumWidth()))

        if maxWidth > column.minimumWidth():
            basicWidth = maxWidth
        else:
            basicWidth = column.minimumWidth()  

        if lineWidth + (basicWidth*2.75) < mainWindow.ui.scrollArea.width(): 
                print("resizing")
                column.setMaximumWidth(int(basicWidth)) 
                sizeRow.append(1)
                lineWidth += basicWidth
        else:
            if not mainWindow.ui.scrollArea.verticalScrollBar().isVisible():
                column.setMaximumWidth(int(mainWindow.ui.scrollArea.width() - lineWidth - finalItemMargin))
            else: 
                print("Test width: " + str(lineWidth + basicWidth))
                print("Area width: " + str(mainWindow.ui.scrollArea.width()))
                print("Item Width: " + str(basicWidth))
                print("The difference between the end and the last element: " + str(lineWidth + basicWidth - mainWindow.ui.scrollArea.width()))
                if -(lineWidth + basicWidth - mainWindow.ui.scrollArea.width()) < basicWidth*1.75:
                    print("Stretch")
                    sizeRow.append(1.5)
                    sizeRow = []
                    sizeMatrix.append(sizeRow)
                    column.setMaximumWidth(int(mainWindow.ui.scrollArea.width() - lineWidth - finalItemMargin))
                else: 
                    print("There is space")
                    print("The difference between the end and the last element: " + str(lineWidth + basicWidth - mainWindow.ui.scrollArea.width()))
                    column.setMaximumWidth(int(basicWidth)) 
                    sizeRow.append(2)
                    sizeMatrix.append(sizeRow)
                    sizeRow = []
                lineWidth = 0
        print("Items in column: " + str(column.layout().count()))

        print("Layout height: " + str(column.layout().sizeHint().height()))
        print("Widget height: " + str(column.height()))

        print("LineWidth: " + str(lineWidth))
        
        print("Items in column: " + str(column.layout().count()))
        print("Column margins: " + str(column.layout().setContentsMargins(0, 0, 0, 0)))
        print("Column spacing: " + str(column.layout().setSpacing(0)))
    
    for column in columnWidgets:
        newFlow.addWidget(column)
        
    mainWindow.ui.flowBoi = newFlow
    newWidge.setLayout(newFlow)
    newWidge.layout()._hspacing = 0
    newWidge.layout()._vspacing = 0
    
    return newWidge

def generateContent(contentDirectory, mainWindow):
    contentFilenames = os.listdir(contentDirectory)
            
    content = []
    print("Number of elements: " + str(len(contentFilenames)))
    contentNumber = 0
    vidNumber = 0

    for image in contentFilenames:
        
        imagePath = os.path.join(contentDirectory, image)
        if not imagePath.endswith(('.mp4', '.gif')):
            print("Image " + image + " is being processed." + " " + str(contentNumber))

            image = generateImageWidget(contentDirectory ,imagePath, image, mainWindow.ui, mainWindow)

            content.append(image)
        elif imagePath.endswith('.mp4'):
            print("Video " + image + " is being processed. " + " " + str(contentNumber))

            videoWidget = generateVideoWidget(contentDirectory, imagePath, image, vidNumber, mainWindow.ui.videoplayers, mainWindow.ui.playlists, mainWindow.ui)

            content.append(videoWidget)
            vidNumber += 1
        else:
            print("Gif " + image + " is being processed. " + " " + str(contentNumber))

            gif = generateGifWidget(contentDirectory, imagePath, image, mainWindow.ui)

            content.append(gif)

        contentNumber += 1

    return content

def generateContentThreaded(contentDirectory, mainWindow, contentSignal, pagesAvailableSignal, currentPage, contentFilenames):
    if contentFilenames == None:
        contentFilenames = os.listdir(contentDirectory)
        contentFilenames.sort(key=lambda filepath: os.path.getctime(os.path.join(contentDirectory, filepath)))
            
    content = []
    print("Number of elements: " + str(len(contentFilenames)))
    contentNumber = 0
    vidNumber = 0

    combinedExtensions = []
    combinedExtensions.append(videoExtension)
    combinedExtensions.append(gifExtension)

    # vidsInFolder = [file for file in contentFilenames if any(extension in file for extension in combinedExtensions) ]

    # vidCount = len(vidsInFolder)
    # vidLimit = 20
    # if vidCount > vidLimit:
    #     print("Too many vids!")
    #     lastVideo = vidsInFolder[vidLimit + 1]
    #     lastVideoIndex = contentFilenames.index(lastVideo)
    #     print(f"Getting {lastVideoIndex} content")
    #     contentFilenames = contentFilenames[:lastVideoIndex]

    numberOfPagesAvailable = len(contentFilenames)/20

    pagesAvailableSignal.emit(numberOfPagesAvailable + 1)

    nextPage = currentPage * 20 + 20

    if len(contentFilenames) > 20: contentFilenames = contentFilenames[currentPage*20:nextPage]

    for image in contentFilenames:
        
        imagePath = os.path.join(contentDirectory, image)
        contentSignal.emit(imagePath, image, contentDirectory)
        #print("In loop:" + str(contentNumber))
        contentNumber += 1