from PySide import QtGui, QtCore
from SearcherLite import *
from ListDelegate import *
if sys.platform not in ['win32','darwin']:
    from LinuxFileOpener import *
import os, sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

iconfolder = os.path.join(program_location,'Icons')

MUSIC_EXT = ['.mp3','.flac','.wav','.wma','.m4a','.aiff','.m4p']
IMAGE_EXT = ['.jpeg','.jpg','.bmp','.tiff','.png','.psd','gif','.jfif','.exif','.']
TXT_LIST = ['.txt', '.ini']
SRC_LIST = ['.c','.cpp','.py','.java','.h','.hpp', '.php', '.sql']
VIDEO_EXT = ['.avi','.mp4','.mpeg','.mov','.wma','.wmv','.wmx','.ogm','.mkv']
MODEL_LIST = ['.max','.mb','.ma']
ARCHIVE_LIST = ['.zip', '.rar','.7z', '.tar', '.gz', '.tar.gz']


fileicon = os.path.join(iconfolder, 'file.png')
foldericon = os.path.join(iconfolder, 'folder.png')
musicicon = os.path.join(iconfolder, 'music.png')
archiveicon = os.path.join(iconfolder, 'archive.png')
texticon = os.path.join(iconfolder, 'txt.png')
dmgicon = os.path.join(iconfolder, 'dmg.png')
docicon = os.path.join(iconfolder, 'doc.png')
epubicon = os.path.join(iconfolder, 'epub.png')
mobiicon = os.path.join(iconfolder, 'mobi.png')
pdficon = os.path.join(iconfolder, 'PDF.png')
videoicon = os.path.join(iconfolder, 'video.png')
xmlicon = os.path.join(iconfolder, 'xml.png')
srcicon = os.path.join(iconfolder, 'src.png')
modelicon = os.path.join(iconfolder, '3D.png')
cssicon = os.path.join(iconfolder, 'css.png')
exeicon = os.path.join(iconfolder, 'exe.png')
htmlicon = os.path.join(iconfolder, 'html.png')
objicon = os.path.join(iconfolder, 'obj.png')

class ResultWindow(QtGui.QWidget):
    def __init__(self, parent = None):
        super(ResultWindow,self).__init__()
        self.Searcher = parent
        self.menu = QtGui.QMenu(self)
        if sys.platform not in ['win32','darwin']:
            self.lfo = LinuxFileOpener()
        self.y =0
        self.initUI()

    def initUI(self):
        self.is_preview_open = False

        layout = QtGui.QVBoxLayout(self)
        self.listwidget = QtGui.QListWidget(self)
        layout.addWidget(self.listwidget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.listwidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listwidget.itemSelectionChanged.connect(self.previewing)
        self.listwidget.doubleClicked.connect(self.OpenFile)

        # shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Backspace), self.listwidget)
        # shortcut.activated.connect(self.Searcher.delete)

        # shortcut2 = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.listwidget)
        # shortcut2.activated.connect(self.Searcher.delete)

        action = QtGui.QAction('focus right',self)
        action.setShortcut("R")
        action.triggered.connect(self.focusTextRight)

        action2 = QtGui.QAction('focus left', self)
        action2.setShortcut("G")
        action2.triggered.connect(self.focusTextLeft)

        action3 = QtGui.QAction('focus right highlight', self)
        action3.setShortcut("V")
        action3.triggered.connect(self.focusTextLeftHigh)

        CopyPathAction = QtGui.QAction('Copy Path',self)
        CopyPathAction.setShortcut("C")
        CopyPathAction.triggered.connect(self.copyPath)    

        self.addAction(action)
        self.addAction(action2)
        self.addAction(action3)
        self.addAction(CopyPathAction)

        self.setGeometry(self.Searcher.pos().x() + 21, self.Searcher.pos().y() + 125, 780, 50)
        self.setAutoFillBackground(True)
        self.setPalette(QtCore.Qt.white)

        self.setWindowTitle("Searcher")
        self.setMinimumHeight(40)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowOpacity(0.85)

        self.createAction()

    def focusTextLeftHigh(self):
        self.Searcher.activateWindow()
        self.Searcher.setFocus()
        self.Searcher.line_edit.setFocus()

    def focusTextRight(self):
        self.Searcher.activateWindow()
        self.Searcher.setFocus()
        self.Searcher.deep_line.setFocus()

    def focusTextLeft(self):
        self.Searcher.activateWindow()
        self.Searcher.setFocus()
        self.Searcher.line_edit.setFocus()
        self.Searcher.line_edit.deselect()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()
        if event.key() == QtCore.Qt.Key_Control:
            self.Searcher.activateWindow()
            self.Searcher.setFocus()
            self.Searcher.line_edit.setFocus()
            self.Searcher.line_edit.deselect()

        if event.key() == QtCore.Qt.Key_Return:
            self.OpenFile()

    def updateSize(self, checktextfromresult=False):
        height = QtGui.QDesktopWidget().availableGeometry().height()
        height = (height - height%100)/2
        height = height + 5
        self.y = 5+len(self.Searcher.found)*25
        if self.y > height: self.y=height
        self.resize(self.Searcher.size().width()-20, self.y)
        counter = 0
        total = len(self.Searcher.found)
        if not checktextfromresult:
            for item in self.Searcher.found:
                if not self.isVisible(): break
                if counter%100==0:
                    self.Searcher.status_label.setText("Status: Drawing "+ str(counter) + ' of ' +str(total) + " Result Tiles...Please Wait ")
                    QtGui.QApplication.processEvents()
                counter +=1
                if self.Searcher.option !=2:
                    self.updateWidget(item)
                else:
                    if item not in self.Searcher.hiddenlist:
                        self.updateWidget(item)
        self.y = 5 + self.listwidget.count() * 25


    def updateSizeChange(self):
        self.resize(self.Searcher.size().width()-20, self.y)


    def updateLoc(self):
        if sys.platform =='win32':
            self.move(QtCore.QPoint(self.Searcher.pos().x() + 10, self.Searcher.pos().y() + 55))
        else:
            self.move(QtCore.QPoint(self.Searcher.pos().x() + 10, self.Searcher.pos().y() + 67))
        height = QtGui.QDesktopWidget().availableGeometry().height()
        height = (height - height%100)/2
        height = height + 5
        if self.y > height: self.y = height 
        self.resize(self.Searcher.size().width()-20, self.y)



    def createAction(self):
        CopyAction = QtGui.QAction('Copy file to target location', self)
        CopyAction.triggered.connect(self.Searcher.CopyFiles)

        MoveAction = QtGui.QAction('Move file to target location', self)
        MoveAction.triggered.connect(self.Searcher.MoveFiles)

        ShowDirAction = QtGui.QAction('Show folders only', self)
        ShowDirAction.triggered.connect(self.ShowDirOnly)

        ShowFilesAction = QtGui.QAction('Show files only', self)
        ShowFilesAction.triggered.connect(self.ShowFilesOnly)

        self.ShowHiddenAction = QtGui.QAction('Show Hiddens only',self)
        self.ShowHiddenAction.triggered.connect(self.showHiddenOnly)

        self.HideHiddenAction = QtGui.QAction('Hide Hidden', self)
        self.HideHiddenAction.triggered.connect(self.HideHidden)

        ShowAllAction = QtGui.QAction('Show all', self)
        ShowAllAction.triggered.connect(self.ShowAll)

        OpenFileAction = QtGui.QAction('Open File', self)
        OpenFileAction.triggered.connect(self.OpenFile)

        # grepAction = QtGui.QAction('Grep',self)
        # grepAction.triggered.connect(self.grep)

        self.openHighlightAction = QtGui.QAction('Open and Highlight',self)
        self.openHighlightAction.triggered.connect(self.openText)

        self.previewAction = QtGui.QAction("Preview",self)
        self.previewAction.triggered.connect(self.preview)

        deleteAction = QtGui.QAction("&Delete", self)
        deleteAction.triggered.connect(self.Searcher.delete)

        OpenContainFolderAction = QtGui.QAction('Open containing folder', self)
        OpenContainFolderAction.triggered.connect(self.OpenContainerFolder)

        CopyPathAction = QtGui.QAction('Copy Path',self)
        CopyPathAction.triggered.connect(self.copyPath)      

        CopyFolderPathAction = QtGui.QAction('Copy Folder Path',self)
        CopyFolderPathAction.triggered.connect(self.copyFolderPath)  

        #self.menu.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.menu.addAction(self.previewAction)
        #self.menu.addAction(playAction)
        self.menu.addAction(OpenFileAction)
        self.menu.addAction(OpenContainFolderAction)
        self.menu.addAction(self.openHighlightAction)
        #self.menu.addAction(grepAction)
        self.menu.addSeparator()
        self.menu.addAction(ShowAllAction)
        self.menu.addAction(ShowDirAction)
        self.menu.addAction(ShowFilesAction)
        self.menu.addAction(self.ShowHiddenAction)
        self.menu.addAction(self.HideHiddenAction)
        self.menu.addSeparator()
        self.menu.addAction(CopyPathAction)
        self.menu.addAction(CopyFolderPathAction)
        self.menu.addSeparator()
        self.menu.addAction(CopyAction)
        self.menu.addAction(MoveAction)
        #self.menu.addAction(deleteAction)

    def contextMenuEvent(self,event):
        for item in self.listwidget.selectedItems():
            item= item.text()
            ext = os.path.splitext(item)[-1].lower()
            if ext not in IMAGE_EXT:
                self.previewAction.setVisible(False)
            else:
                self.previewAction.setVisible(True)
        if self.Searcher.option ==1:
            self.ShowHiddenAction.setVisible(False)
            self.HideHiddenAction.setVisible(False)
        else:
            self.ShowHiddenAction.setVisible(True)
            self.HideHiddenAction.setVisible(True)
        if self.Searcher.deep_line.text()=='':
            self.openHighlightAction.setVisible(False)
        else:
            self.openHighlightAction.setVisible(True)
        self.menu.exec_(event.globalPos())

    def updateWidget(self,item):
        self.listwidget.setItemDelegate(ListDelegate(self.listwidget))
        list_item = QtGui.QListWidgetItem()
        if sys.platform =='win32':
            list_item.setData(QtCore.Qt.UserRole, item[item.rfind('\\')+1:])
        else:
            list_item.setData(QtCore.Qt.UserRole, item[item.rfind('/')+1:])
        list_item.setData(QtCore.Qt.DisplayRole,item)
        if os.path.isdir(item):
            list_item.setData(QtCore.Qt.DecorationRole,foldericon)
        elif os.path.isfile(item):
            ext = os.path.splitext(item)[-1].lower()
            if ext in MUSIC_EXT:
                list_item.setData(QtCore.Qt.DecorationRole,musicicon)
            elif ext in TXT_LIST:
                list_item.setData(QtCore.Qt.DecorationRole,texticon)
            elif ext in ARCHIVE_LIST:
                list_item.setData(QtCore.Qt.DecorationRole,archiveicon) 
            elif ext in VIDEO_EXT:
                list_item.setData(QtCore.Qt.DecorationRole, videoicon)
            elif ext in MODEL_LIST:
                list_item.setData(QtCore.Qt.DecorationRole,modelicon)
            elif ext in SRC_LIST:
                list_item.setData(QtCore.Qt.DecorationRole,srcicon)
            elif ext == '.mobi':
                list_item.setData(QtCore.Qt.DecorationRole, mobiicon)
            elif ext == '.epub':
                list_item.setData(QtCore.Qt.DecorationRole, epubicon)
            elif ext == '.xml':
                list_item.setData(QtCore.Qt.DecorationRole, xmlicon)
            elif ext == '.pdf':
                list_item.setData(QtCore.Qt.DecorationRole, pdficon)
            elif ext == '.dmg':
                list_item.setData(QtCore.Qt.DecorationRole, dmgicon)
            elif ext == '.obj':
                list_item.setData(QtCore.Qt.DecorationRole,objicon)
            elif ext == '.css':
                list_item.setData(QtCore.Qt.DecorationRole,cssicon)
            elif ext == '.exe':
                list_item.setData(QtCore.Qt.DecorationRole,exeicon)
            elif ext == '.html':
                list_item.setData(QtCore.Qt.DecorationRole,htmlicon)
            else:   
                list_item.setData(QtCore.Qt.DecorationRole,fileicon)

                
        self.listwidget.addItem(list_item)

    def HideHidden(self):
        self.Searcher.status_label.setText('Status: Drawing Result Tiles... Please Wait')
        counter = 0
        self.listwidget.clear()
        for item in self.Searcher.found:
            if item not in self.Searcher.hiddenlist:
                if counter%50==0:
                    QtGui.QApplication.processEvents()
                self.updateWidget(item)
                counter+=1
        self.Searcher.status_label.setText('Status: Found ' + str(len(self.Searcher.found)) + ' items' + ' Showing: ' + str(self.listwidget.count()))

    def ShowDirOnly(self):
        self.Searcher.status_label.setText('Status: Drawing Result Tiles... Please Wait')
        counter = 0
        self.listwidget.clear()
        for item in self.Searcher.found:
            if counter%50==0:
                QtGui.QApplication.processEvents()
            counter+=1
            if os.path.isdir(item):
                if self.Searcher.option !=2:
                    self.updateWidget(item)
                else:
                    if item not in self.Searcher.hiddenlist:
                        self.updateWidget(item)
        self.Searcher.status_label.setText('Status: Found ' + str(len(self.Searcher.found)) + ' items' + ' Showing: ' + str(self.listwidget.count()))

    def ShowFilesOnly(self):
        self.Searcher.status_label.setText('Status: Drawing Result Tiles... Please Wait')
        counter = 0
        self.listwidget.clear()
        for item in self.Searcher.found:
            if counter%50==0:
                QtGui.QApplication.processEvents()
            counter+=1
            if os.path.isfile(item):
                if self.Searcher.option !=2:
                    self.updateWidget(item)
                else:
                    if item not in self.Searcher.hiddenlist:
                        self.updateWidget(item)
        self.Searcher.status_label.setText('Status: Found ' + str(len(self.Searcher.found)) + ' items' + ' Showing: ' + str(self.listwidget.count()))

    def ShowAll(self):
        self.Searcher.status_label.setText('Status: Drawing Result Tiles... Please Wait')
        counter = 0
        self.listwidget.clear()
        for item in self.Searcher.found:
            if counter%50==0:
                QtGui.QApplication.processEvents()
            self.updateWidget(item)
            counter +=1
        self.Searcher.status_label.setText('Status: Found ' + str(len(self.Searcher.found)) + ' items' + ' Showing: ' + str(self.listwidget.count()))

    def showHiddenOnly(self):
        self.Searcher.status_label.setText('Status: Drawing Result Tiles... Please Wait')
        counter = 0 
        self.listwidget.clear()
        for item in self.Searcher.found:
            if item in self.Searcher.hiddenlist:
                if counter%50==0:
                    QtGui.QApplication.processEvents()
                self.updateWidget(item)
                counter+=1
        self.Searcher.status_label.setText('Status: Found ' + str(len(self.Searcher.found)) + ' items' + ' Showing: ' + str(self.listwidget.count()))

    def OpenContainerFolder(self):
        for item in self.listwidget.selectedItems():
            folder = ''
            if sys.platform == 'win32':
                path = item.text().split('\\')
            else:
                path = item.text().split('/')
            for x in range(len(path) - 1):
                folder = os.path.join(folder, path[x])
            if sys.platform == 'win32':
                os.startfile(folder)
            else:
                subprocess.call(['xdg-open', '/' + folder])

    def copyPath(self):
        clipboard = QtGui.QApplication.clipboard()
        for item in self.listwidget.selectedItems():
            clipboard.setText(item.text())

    def copyFolderPath(self):
        clipboard = QtGui.QApplication.clipboard()
        for item in self.listwidget.selectedItems():
            folder = ''
            if sys.platform == 'win32':
                path = item.text().split('\\')
            else:
                path = item.text().split('/')
            for x in range(len(path) - 1):
                folder = os.path.join(folder, path[x])
            clipboard.setText(folder)

    def previewing(self):
        if self.is_preview_open:
            for item in self.listwidget.selectedItems():
                image = item.text()
            if os.path.splitext(image)[-1].lower() in IMAGE_EXT:
                self.imageview.open(image)

    def preview(self):
        if not self.is_preview_open:
            self.is_preview_open = True
            self.imageview = ImageView(self.filter())
            self.imageview.destroyed.connect(self.previewClosed)
            self.imageview.show()
            for item in self.listwidget.selectedItems():
                image = item.text()
            if os.path.splitext(image)[-1].lower() in IMAGE_EXT:
                self.imageview.open(image)

    def filter(self):
        templist = []
        current = self.Searcher.found[self.listwidget.currentRow()]
        for item in self.Searcher.found:
            ext = os.path.splitext(item)[-1].lower()
            if ext in IMAGE_EXT:
                templist.append(item)
        index = templist.index(current)
        return (templist,index)

    def previewClosed(self):
        self.is_preview_open = False

    def openText(self):
        self.editor = TextEditor()
        if self.Searcher.deep_line != '':
            for item in self.listwidget.selectedItems():
                f = open(item.text(), 'r')
                for line in f:
                    self.editor.textedit.append(line.rstrip('\n'))
                f.close()
                self.editor.highlight(self.Searcher.deep_line.text())
                self.editor.show()


    def grep(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Grep', 'Enter Search Pattern')
        if ok:
            for item in self.listwidget.selectedItems():
                f = open(item.text(), 'r')
                string = []
                for line in f:
                    string.append(line.rstrip('\n'))
                x = 0
                xlist = []
                for item in string:
                    if text in item:
                        xlist.append(x)
                    x += 1

                self.editor = TextEditor()
                for x in xlist:
                    if x > 1:
                        self.editor.textedit.append(string[x - 1])
                    self.editor.textedit.append(string[x])
                    if x < len(string) - 1:
                        self.editor.textedit.append(string[x + 1])
                    self.editor.textedit.append('\n')
                    x += 1

                self.editor.highlight(text)
                self.editor.show()

    def OpenFile(self):
        for item in self.listwidget.selectedItems():
            if sys.platform == 'win32':
                os.startfile(item.text())
            elif sys.platform == 'darwin':
                command = "/usr/bin/open " + item.text().replace(' ','\\ ')
                subprocess.Popen(command,shell=True)
            else:
                if self.lfo.checkList(item.text()):
                    self.lfo.openFile(item.text())
                else:
                    file_type = self.lfo.xdgQuery('filetype',item.text())
                    app = self.inputDialog(file_type)
                    self.lfo.addToList(file_type,app)
                    self.lfo.openFile(item.text())
    
    def inputDialog(self, app_type):
        dia = 'no/invalid default app for: ' + app_type + '-> set one below (ex:gedit)\n (refer to view->app table if you are not sure)'
        text, ok = QtGui.QInputDialog.getText(self, 'set default application', dia)
        if ok:
            if self.checkApps(text):
                return text
            else:
                self.inputDialog(app_type)

    def checkApps(self, text):
        for item in os.listdir(r'/usr/share/applications'):
            if text == item.split('.')[0]:
                return True
        return False