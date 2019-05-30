import os, sys, re
from PySide import QtGui, QtCore
import time
from SettingWindow import *
from ProcessThread import *
from UpdateThread import *
if sys.platform not in ['win32','darwin']:
    from AppTable import *
from TextEditor import *
from ImageView import *
from ResultWindow import *
import getpass
#import docx
if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))
if sys.platform != 'win32': 
    document_location = os.path.join('/home',getpass.getuser(),'.Searcher')
    if not os.path.isdir(document_location):
        os.mkdir(document_location)
else:
    document_location = os.path.join('C:\\Users',getpass.getuser(),'Documents','Searcher')
    if not os.path.isdir(document_location):
        os.mkdir(document_location)

archivefolder = os.path.join(document_location, 'Archive')
if not os.path.isdir(archivefolder):
    os.mkdir(archivefolder)

file_count = os.path.join(archivefolder, 'counts.txt')
export_file = os.path.join(archivefolder, 'foundfiles.txt')
search_locations = os.path.join(archivefolder, 'locations.txt')
path_archive = os.path.join(archivefolder, 'path archive.txt')
hidden_path_archive = os.path.join(archivefolder, 'hidden path archive.txt')
restricted_file = os.path.join(archivefolder, 'restricted folders.txt')
error_log_file = os.path.join(archivefolder, 'error log.txt')
exception_file = os.path.join(archivefolder, 'exception.txt')
settings = os.path.join(archivefolder,'settings.txt')

icon = os.path.join(program_location, 'find.png')
help_file = os.path.join(program_location, 'help.txt')

MAXFILELOAD = 1024 * 15000
BLOCKSIZE = 1024 * 5000
MUSIC_EXT = ['.mp3','.flac','.wav','.wma','.m4a','.aiff','.m4p']
IMAGE_EXT = ['.jpeg','.jpg','.bmp','.tiff','.png','.psd','gif','.jfif','.exif']
VIDEO_EXT = ['.avi','.mp4','.mpeg','.mov','.wma','.wmv','.wmx','.ogm','.mkv']
SRC_LIST = ['.c','.cpp','.py','.java','.h','.hpp','.php','.sql','.html','.thtml','.htm','.css']


EXT_LIST = ['','.txt', '.ini', '.py', '.htm,', '.html', '.thtml', '.php', '.sql','.c','.cpp','.java', '.css']



class Searcher(QtGui.QWidget):
    def __init__(self):
        super(Searcher, self).__init__()
        # variables
        self.mode = ''
        self.option = 3
        self.is_preview_open = False
        self.restricted_dir_count = 0

        # timer
        self.timer = QtCore.QTimer(self)

        # lists
        self.error_list = []
        self.restricted_dir = []
        self.found = []
        self.root_search_list = []
        self.search_exception_list = []
        self.pathlist = []
        self.hiddenlist = []
        self.hiddendirs = []


        # creating widgets
        self.file_lcd = QtGui.QLCDNumber(self)
        self.dir_lcd = QtGui.QLCDNumber(self)
        self.progress_bar = QtGui.QProgressBar(self)
        self.menu = QtGui.QMenu(self)
        self.status_label = QtGui.QLabel('Status: ', self)
        self.line_edit = MyLineEdit(self)
        self.deep_line = MyLineEdit(self)
        self.index_date = QtGui.QLabel(self)
        self.resultwindow = ResultWindow(self)

        self.initUI()


    def initUI(self):
        ico = QtGui.QIcon(icon)

        # menu creations
        self.CreateActionsAndMenu()

        # layouts
        vlaybox = QtGui.QVBoxLayout(self)
        hlaybox = QtGui.QHBoxLayout(self)

        hlaybox.addWidget(self.line_edit)
        hlaybox.addWidget(self.deep_line)


        vlaybox.addWidget(self.progress_bar)

        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.status_label)
        hbox.addStretch()
        hbox.addWidget(self.dir_lcd)
        hbox.addWidget(self.file_lcd)
        hbox.addStretch()
        hbox.addWidget(self.index_date)
        vlaybox.addLayout(hbox)
        vlaybox.addLayout(hlaybox)
        vlaybox.setContentsMargins(3,0,3,3)

        #widget settings
        self.file_lcd.display(0)
        self.dir_lcd.display(0)
        self.dir_lcd.setNumDigits(7)
        self.file_lcd.setNumDigits(9)
        self.status_label.setFixedWidth(350)

        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(3)

        self.dir_lcd.setSegmentStyle(self.dir_lcd.Flat)
        self.file_lcd.setSegmentStyle(self.file_lcd.Flat)

        #connecting signals
        self.line_edit.returnPressed.connect(self.SearchSplit)
        self.deep_line.returnPressed.connect(self.DeepSearch)
        self.timer.timeout.connect(self.Update)

        if os.path.isfile(file_count):
            f = open(file_count, 'r')
            x = 0
            for line in f:
                if x == 0:
                    self.dir_count = int(line.rstrip('\n'))
                    self.dir_lcd.display(self.dir_count)
                else:
                    self.file_count = int(line.rstrip('\n'))
                    self.file_lcd.display(self.file_count)
                x += 1
            f.close()

        #window settings
        self.setGeometry(100, 50, 675, 70)
        self.setWindowTitle("Searcher")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowIcon(ico)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        if sys.platform == 'win32':
            self.setFixedHeight(60)
        self.setStyleSheet("QLabel{font-size: 11px;border-radius: 10px; border: 1px solid rgb(188,188,188,250);} QProgressBar::chunk{background-color: rgba(100,179,255,250)} QFrame{border: 1px solid gray;border-radius: 10px}")
        self.setWindowOpacity(0.9)
        self.center()
        self.show()
        self.Initialize()

    def resizeEvent(self,event):
        self.resultwindow.updateSizeChange()

    def focusInEvent(self,event):
        if self.resultwindow.isVisible():
            self.resultwindow.raise_()

    def moveEvent(self,event):
        if self.resultwindow.isVisible():
            self.resultwindow.updateLoc()
            self.resultwindow.raise_()

    def contextMenuEvent(self,event):
        self.menu.exec_(event.globalPos())

    def mousePressEvent(self,event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if event.pos().x() < self.size().width() -20:
                self.diff = event.globalPos() - self.frameGeometry().topLeft()
                self.mode = 'drag'
            else:
                self.mode = 'resize'
        if self.resultwindow.isVisible():
            self.resultwindow.raise_()


    def mouseMoveEvent(self,event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.mode == 'drag':
                self.move(event.globalPos()-self.diff)
            else:
                self.resize(event.pos().x(),self.size().height())


    def Initialize(self):
        if os.path.isfile(path_archive):
            self.ReadArchive()
            self.index_date.setText('Index -> Last updated: ' + self.pathlist[0])
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText('Status: There is no stored Index, please generate')
            self.index_date.setText('Index -> Last Updated: Never')
        if not os.path.isfile(exception_file):
            f = open(exception_file, 'w+')
            f.write('')
            f.close()
        if os.path.isfile(settings):
            self.readSettings()
        else:
            f = open(settings,'w+')
            f.write('0\n')
            f.write('off\n')
            f.write('1')
            f.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()-QtCore.QPoint(0,200))


    def readSettings(self):
        f = open(settings,'r')
        setting = []
        for line in f:
            setting.append(line.rstrip('\n'))
        if int(setting[0])>0:
            self.timer.setInterval(int(time[0]))
            self.timer.start()
        if setting[1] =='on':
            self.Update()
        self.option = int(setting[2])
        f.close()

    def setTimer(self):
        f = open(settings,'r')
        time = []
        for line in f:
            time.append(line.rstrip('\n'))
        if int(time[0])>0:
            self.timer.setInterval(int(time[0]))
            self.timer.start()
        else:
            self.timer.stop()
        f.close()

    def closeEvent(self, event):
        try:
            self.setting.close()
        except Exception:
            pass
        try:
            self.resultwindow.close()
        except Exception:
            pass
        try:
            self.resultwindow.imageview.close()
        except Exception:
            pass



    def CreateActionsAndMenu(self):
        generateAction = QtGui.QAction('Generate',self)
        generateAction.setShortcut("Ctrl+G")
        generateAction.triggered.connect(self.GenerateArchive)

        exitaction = QtGui.QAction('Exit', self)
        exitaction.setShortcut('Ctrl+Q')
        exitaction.triggered.connect(self.close)
        self.addAction(exitaction)

        ExportAction = QtGui.QAction('Export found files', self)
        ExportAction.setShortcut('Ctrl+E')
        ExportAction.triggered.connect(self.ExportFound)

        ShowExportAction = QtGui.QAction('Open Recent Exported File', self)
        ShowExportAction.setShortcut('Ctrl+O')
        ShowExportAction.triggered.connect(self.ShowExport)

        ShowRestrictedAction = QtGui.QAction('Show Inaccessible Folders', self)
        ShowRestrictedAction.triggered.connect(self.OpenRestricted)

        ResetAction = QtGui.QAction('Reset', self)
        ResetAction.setShortcut('Ctrl+R')
        ResetAction.triggered.connect(self.Reset)

        # ShowHelpAction = QtGui.QAction('Manual', self)
        # self.ShowHelpAction.triggered.connect(self.ShowManual)

        # ShowChangeAction = QtGui.QAction('Change Log', self)
        # self.ShowChangeAction.triggered.connect(self.ShowChangeLog)


        LaunchSettingAction = QtGui.QAction('Settings', self)
        LaunchSettingAction.setShortcut("Ctrl+S")
        LaunchSettingAction.triggered.connect(self.LaunchSettings)

        if sys.platform not in ['win32','darwin']:
            LaunchAppTableAction = QtGui.QAction('Desktop Table', self)
            LaunchAppTableAction.triggered.connect(self.LaunchAppTable)

        LaunchTextAction = QtGui.QAction('Text Editor', self)
        LaunchTextAction.setShortcut('Ctrl+T')
        LaunchTextAction.triggered.connect(self.LaunchTextEditor)


        self.addAction(generateAction)
        self.addAction(ExportAction)
        self.addAction(ShowExportAction)
        self.addAction(ShowRestrictedAction)
        self.addAction(LaunchSettingAction)
        self.addAction(ResetAction)
        if sys.platform not in ['win32','darwin']:
            self.addAction(LaunchAppTableAction)
        self.addAction(LaunchTextAction)
        self.addAction(exitaction)


        self.menu.addAction(generateAction)
        self.menu.addAction(ExportAction)
        self.menu.addAction(ShowExportAction)
        self.menu.addAction(ShowRestrictedAction)
        self.menu.addSeparator()
        self.menu.addAction(LaunchSettingAction)
        self.menu.addSeparator()
        self.menu.addAction(ResetAction)
        self.menu.addSeparator()
        if sys.platform not in ['win32','darwin']:
            self.menu.addAction(LaunchAppTableAction)
        self.menu.addAction(LaunchTextAction)
        self.menu.addSeparator()
        self.menu.addAction(exitaction)

    def delete(self):
        del_list = []
        for item in self.resultwindow.listwidget.selectedItems():
            del_list.append(item.text())
        more_info = ""
        for path in del_list:
            more_info += path + "\n"
        if del_list != []:
            messagebox = QtGui.QMessageBox()
            messagebox.setText("Are you sure you want to delete these items?")
            messagebox.setDetailedText("** "+more_info)
            messagebox.setStandardButtons(QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            ret = messagebox.exec_()
            if ret == QtGui.QMessageBox.Yes:
                for path in del_list:
                    if os.path.isfile(path):
                        os.remove(path)
                        self.pathlist.remove(path)
                        self.found.remove(path)
                        self.file_count -=1
                    if os.path.isdir(path):
                        if os.listdir(path)==[]:
                            os.rmdir(path)
                            self.pathlist.remove(path)
                            self.found.remove(path)
                            self.dir_count -=1
                        else:
                            self.deleteDir(path)
                            os.rmdir(path)
                            self.pathlist.remove(path)
                            self.found.remove(path)
                            self.dir_count -=1
                self.resultwindow.listwidget.clear()
                for item in self.found:
                    self.resultwindow.listwidget.addItem(item)
                self.status_label.setText("Status: Found " + str(len(self.found)) + " items")
                self.file_lcd.display(self.file_count)
                self.dir_lcd.display(self.dir_count)
                self.CreateArchive()


    def deleteDir(self,path):
        for item in os.listdir(path):
            item = os.path.join(path,item)
            if os.path.isfile(item):
                os.remove(item)
                self.pathlist.remove(item)
                if item in self.found:
                    self.found.remove(item)
                self.file_count -=1
            else:
                if os.listdir(item)==[]:
                    os.rmdir(item)
                    self.pathlist.remove(item)
                    if item in self.found:
                        self.found.remove(item)
                    self.dir_count-=1
                else:
                    self.deleteDir(item)


    def LaunchTextEditor(self):
        self.texteditor = TextEditor()
        self.texteditor.show()

    def LaunchAppTable(self):
        self.table = AppTable()
        self.table.show()


    def Update(self):
        self.status_label.setText("Status: Updating Index")
        thread = UpdateThread()
        self.pathlist, self.file_count, self.dir_count = thread.run()
        self.file_lcd.display(self.file_count)
        self.dir_lcd.display(self.dir_count)
        self.status_label.setText('Status: Index Updated!')
        self.index_date.setText('Index -> Last Updated: ' + self.pathlist[len(self.pathlist)-1])

    def TotalSize(self):
        size = 0
        for path in self.pathlist:
            if not os.path.isdir(path):
                size += os.path.getsize(path)
        return size

    def LaunchSettings(self):
        pos = self.pos()
        self.is_setting_open = True
        self.setting = SettingsWindow(pos.x() + 8, pos.y()-300)
        self.setting.destroyed.connect(self.setTimer)
        self.setting.destroyed.connect(self.readSettings)
        self.setting.save_button.clicked.connect(self.setTimer)
        self.setting.save_button.clicked.connect(self.readSettings)


    def CopyFiles(self):
        dialog = QtGui.QFileDialog(self)
        target_dir = dialog.getExistingDirectory()
        processed_data = 0
        total_data = 0
        for item in self.resultwindow.listwidget.selectedItems():
            total_data += os.path.getsize(item.text())
        for item in self.resultwindow.listwidget.selectedItems():
            goodloc = True
            if sys.platform == 'win32':
                filename = item.text().split('\\')[-1]
            else:
                filename = item.text().split('/')[1]

            path_to = os.path.join(target_dir, filename)
            file_from = open(item.text(), 'rb')
            bytes_to = open(path_to, 'wb')
            if os.path.getsize(item.text()) <= MAXFILELOAD:
                try:
                    bytes_from = file_from.read()
                    bytes_to.write(bytes_from)
                except Exception:
                    self.error_list.append('error copying file:' + item.text())
                    goodloc = False
            else:
                while True:
                    try:
                        bytes_from = file_from.read(BLOCKSIZE)
                        if not bytes_from: break
                        bytes_to.write(bytes_from)
                    except Exception:
                        self.error_list.append('error copying file:' + item.text())
                        goodloc = False
            processed_data += os.path.getsize(item.text())
            self.status_label.setText(
                'Status: Copying Progress: ' + str(int((processed_data / total_data) * 100)) + '%')
            QtGui.QApplication.processEvents()
            self.progress_bar.setValue(int(processed_data / total_data) * 100)

            file_from.close()
            bytes_to.close()
            if goodloc:
                self.pathlist.append(path_to)
        self.CreateArchive()

    def MoveFiles(self):
        dialog = QtGui.QFileDialog(self)
        target_dir = dialog.getExistingDirectory()
        counter = 0
        for item in self.resultwindow.listwidget.selectedItems():
            if sys.platform == 'win32':
                filename = item.text().split('\\')[-1]
            else:
                filename = item.text().split('/')[1]
            path_to = os.path.join(target_dir, filename)
            try:
                os.renames(item.text(), path_to)
                self.pathlist.remove(item.text())
                self.pathlist.append(path_to)
            except Exception:
                self.error_list.append('error moving file:' + item.text())
            counter += 1
            self.status_label.setText(
                'Status: Moving Progess -> ' + str(counter) + ' out of ' + str(len(self.resultwindow.listwidget.selectedItems())))
            QtGui.QApplication.processEvents()
            self.progress_bar.setValue(100 * (counter / len(self.resultwindow.listwidget.selectedItems())))
        self.CreateArchive()




    def Reset(self):
        f = open(locations, 'w+')
        f.write('')
        f.close()
        f = open(exception_file, 'w+')
        f.write('')
        f.close()
        f = open(file_count, 'w+')
        f.write('')
        f.close()
        self.dir_lcd.display(0)
        self.file_lcd.display(0)


    def ExportFound(self):
        file_dialog = QtGui.QFileDialog(self)
        target = file_dialog.getSaveFileName()
        f = open(target[0], 'w+')
        try:
            for item in self.found:
                f.write(item)
                f.write('\n')
        except UnicodeEncodeError:
            print('error writing')
        f.close()
        f = open(export_file, 'w+')
        try:
            for item in self.found:
                f.write(item)
                f.write('\n')
        except UnicodeEncodeError:
            print('error writing')
        f.close()

    def ShowExport(self):
        if os.path.isfile(export_file):
            if sys.platform == 'win32':
                os.startfile(export_file)
            else:
                subprocess.call(['xdg-open', export_file])
        else:
            self.status_label.setText('Status: No export file, Export file first')


    def GetSetting(self):
        self.root_search_list = []
        self.search_exception_list = []
        f = open(search_locations, 'r')
        for line in f:
            self.root_search_list.append(line.rstrip('\n'))
        f.close()
        f = open(exception_file, 'r')
        for line in f:
            self.search_exception_list.append(line.rstrip('\n'))
        f.close()

    def SubCrawler(self, dir):
        QtGui.QApplication.processEvents()
        try:
            for filename in os.listdir(dir):
                path = os.path.join(dir, filename)
                if path not in self.search_exception_list:
                    # if the path is not a directory, then add it to the list
                    if not os.path.isdir(path):
                        self.pathlist.append(path)
                        self.file_count += 1
                    else:
                        # if it is a directory, we must dive deeper
                        self.pathlist.append(path)
                        self.dir_count += 1
                        self.SubCrawler(path)
                    if self.progress ==100: self.progress = 0
                    self.progress+=1
                    if self.progress%25==0:
                        self.progress_bar.setValue(self.progress)
        except Exception:
            print('encountered an error with dir: ' + dir)

            self.restricted_dir.append(dir)
            self.restricted_dir_count += 1

    def SubCrawlerP1(self, dir):
        QtGui.QApplication.processEvents()
        try:
            for filename in os.listdir(dir):
                path = os.path.join(dir, filename)
                if path not in self.search_exception_list:
                    # if the path is not a directory, then add it to the list
                    info = QtCore.QFileInfo(path)
                    if not os.path.isdir(path):
                        if not info.isHidden():
                            self.pathlist.append(path)
                        else:
                            self.hiddenlist.append(path)
                        self.file_count += 1
                    else:
                        # if it is a directory, we must dive deeper
                        if not info.isHidden():
                            self.pathlist.append(path)
                            self.dir_count += 1
                            self.SubCrawlerP1(path)
                        else:
                            self.hiddenlist.append(path)
                            self.dir_count+=1
                            self.hiddendirs.append(path)
                    if self.progress ==100: self.progress = 0
                    self.progress+=1
                    if self.progress%25==0:
                        self.progress_bar.setValue(self.progress)
        except Exception:
            self.restricted_dir.append(dir)

    def SubCrawlerHidden(self,dir):
        QtGui.QApplication.processEvents()
        try:
            for filename in os.listdir(dir):
                path = os.path.join(dir, filename)
                if path not in self.search_exception_list:
                    # if the path is not a directory, then add it to the list
                    if not os.path.isdir(path):
                        self.hiddenlist.append(path)
                        self.file_count += 1
                    else:
                        # if it is a directory, we must dive deeper
                        self.hiddenlist.append(path)
                        self.dir_count += 1
                        self.SubCrawlerHidden(path)
                    if self.progress ==100: self.progress = 0
                    self.progress+=1
                    if self.progress%25==0:
                        self.progress_bar.setValue(self.progress)
        except Exception:
            self.restricted_dir.append(dir)

    def SubCrawlerNoHidden(self, dir):
        QtGui.QApplication.processEvents()
        try:
            for filename in os.listdir(dir):
                path = os.path.join(dir, filename)
                if path not in self.search_exception_list:
                    # if the path is not a directory, then add it to the list
                    info = QtCore.QFileInfo(path)
                    if not os.path.isdir(path):
                        if not info.isHidden():
                            self.pathlist.append(path)
                            self.file_count += 1
                    else:
                        # if it is a directory, we must dive deeper
                        if not info.isHidden():
                            self.pathlist.append(path)
                            self.dir_count += 1
                            self.SubCrawlerNoHidden(path)
                    if self.progress ==100: self.progress = 0
                    self.progress+=1
                    if self.progress%25==0:
                        self.progress_bar.setValue(self.progress)
        except Exception:
            self.restricted_dir.append(dir)
        

    def MainCrawler(self):
        self.progress = 0
        start = time.time()
        if self.option == 1:
            for item in self.root_search_list:
                self.status_label.setText('Status: Generating Path Index... [' + item + ']')
                self.SubCrawlerNoHidden(item)
        else:
            for item in self.root_search_list:
                self.status_label.setText('Status: Generating Path Index... [' + item + ']')
                self.SubCrawlerP1(item)
            for item in self.hiddendirs:
                self.status_label.setText('Status: Generating Path Index... [hiddens]')
                self.SubCrawlerHidden(item)
        self.pathlist.append(QtCore.QDateTime().currentDateTime().toString('MM.dd.yyyy - hh:mm:ss AP'))
        self.index_date.setText('Index -> Last updated: ' + self.pathlist[-1])
        self.progress_bar.setValue(100)
        end = time.time()
        print(end-start)

    

    def SearchSplit(self):
        self.resultwindow.listwidget.clear()
        self.found = []
        if len(self.line_edit.text().split('|'))>1:
            term= self.line_edit.text().split('|')[0]
            text = self.line_edit.text()
            text = text[text.find('|')+1:]
            term2 = text.split('|')
            self.MultiSearch(term)
            for keys in term2:
                if keys!='':
                    self.SecondarySearch(keys)
        elif self.line_edit.text() == "@musics":
            for path in self.pathlist:
                ext = os.path.splitext(path)[-1].lower()
                if ext in MUSIC_EXT:
                    self.found.append(path)
            if self.option !=1:
                for path in self.hiddenlist:
                    ext = os.path.splitext(path)[-1].lower()
                    if ext in MUSIC_EXT:
                        self.found.append(path)

        elif self.line_edit.text() == "@videos":
            for path in self.pathlist:
                ext = os.path.splitext(path)[-1].lower()
                if ext in VIDEO_EXT:
                    self.found.append(path)
            if self.option !=1:
                for path in self.hiddenlist:
                    ext = os.pat.splitext(path)[-1].lower()
                    if ext in VIDEO_EXT:
                        self.found.append(path)
        elif self.line_edit.text() == "@images":
            for path in self.pathlist:
                ext = os.path.splitext(path)[-1].lower()
                if ext in IMAGE_EXT:
                    self.found.append(path)
            if self.option !=1:
                for path in self.hiddenlist:
                    ext = os.path.splitext(path)[-1].lower()
                    if ext in IMAGE_EXT:
                        self.found.append(path)
        elif self.line_edit.text() == "@srcs":
            for path in self.pathlist:
                ext = os.path.splitext(path)[-1].lower()
                if ext in SRC_LIST:
                    self.found.append(path)
            if self.option !=1:
                for path in self.hiddenlist:
                    ext = os.path.splitext(path)[-1].lower()
                    if ext in SRC_EXT:
                        self.found.append(path)
        elif self.line_edit.text() == '':
            #self.resultwindow.listwidget.clear()
            self.found = []
            self.status_label.setText('Status: Cleared')  
        else:
            term = self.line_edit.text()
            self.MultiSearch(term)

        if self.line_edit.text() !='':
            self.resultwindow.show()
            self.resultwindow.activateWindow() 
            self.resultwindow.updateLoc()
            self.resultwindow.updateSize()
            self.resultwindow.updateLoc()
                   
        if self.line_edit.text() =='' or len(self.found)==0:
            self.resultwindow.hide()
        if len(self.line_edit.text().split(' ; '))== 1 or len(self.line_edit.text().split(' , '))==1:
            if len(self.found) == 0 and self.line_edit.text() != '':
                self.status_label.setText('Status: None Found...')
            if len(self.found) > 0:
                if self.resultwindow.isVisible():
                    self.status_label.setText('Status: Found ' + str(len(self.found)) + ' items' + ' Showing: ' + str(self.resultwindow.listwidget.count()))
                else:
                    self.status_label.setText('Status: Stopped... ready for new search')


    def MultiSearch(self,term):
        if len(term.split(' ; ')) > 1 or len(term.split(' , ')) > 1:
            self.status_label.setText('Status: Please have no spaces for delimiters')
        elif len(term.split(';')) > 1 and '@' not in term:  # and filter
            filt = term.split(';')
            x = 1
            for fil in filt:
                templist = []
                if fil != '':
                    if x == 1:
                        for path in self.pathlist:
                            if fil.lower() in path.lower():
                                self.found.append(path)
                        if self.option != 1:
                            for path in self.hiddenlist:
                                if fil.lower() in path.lower():
                                    self.found.append(path)
                        x += 1
                    else:
                        for path in self.found:
                            if fil.lower() in path.lower():
                                templist.append(path)
                        self.found = []
                        for item in templist:
                            self.found.append(item)

        elif len(term.split(',')) > 1 and '@' not in term:  # or filter
            filt = term.split(',')

            for path in self.pathlist:
                for fil in filt:
                    if fil.lower() in path.lower():
                        if path not in self.found:
                            self.found.append(path)
            if self.option !=1:
                for path in self.hiddenlist:
                    for fil in filt:
                        if fil.lower() in path.lower():
                            if path not in self.found:
                                self.found.append(path)

        elif len(self.line_edit.text().split('@'))>1:
            self.hit = []
            type_ = self.line_edit.text().split("@")[1]
            search_key = self.line_edit.text().split("@")[0]
            if len(search_key.split(','))>1:
                filt = search_key.split(',')
                for path in self.pathlist:
                    for fil in filt:
                        if fil.lower() in path.lower():
                            if path not in self.hit:
                                self.hit.append(path)
                if self.option !=1:
                    for path in self.hiddenlist:
                        for fil in filt:
                            if fil.lower() in path.lower():
                                if path not in self.hit:
                                    self.hit.append(path)
            elif len(search_key.split(';'))>1:
                filt = search_key.split(';')
                x = 1
                for fil in filt:
                    templist = []
                    if fil != '':
                        if x == 1:
                            for path in self.pathlist:
                                if fil.lower() in path.lower():
                                    self.hit.append(path)
                            if self.option !=1:
                                for path in self.hiddenlist:
                                    if fil.lower() in path.lower():
                                        self.hit.append(path)
                            x += 1
                        else:
                            for path in self.hit:
                                if fil.lower() in path.lower():
                                    templist.append(path)
                            self.hit = []
                            for item in templist:
                                self.hit.append(item)
            else:
                for path in self.pathlist:
                    if search_key.lower() in path.lower():
                        self.hit.append(path)
                if self.option !=1:
                    for path in self.hiddenlist:
                        if search_key.lower() in path.lower():
                            self.hit.append(path)
            if type_ =='musics':
                for item in self.hit:
                    if os.path.splitext(item)[-1].lower() in MUSIC_EXT:
                        self.found.append(item)
            elif type_ == 'videos':
                for item in self.hit:
                    if os.path.splitext(item)[-1].lower() in VIDEO_EXT:
                        self.found.append(item)
            elif type_ == 'images':
                for item in self.hit:
                    if os.path.splitext(item)[-1].lower() in IMAGE_EXT:
                        self.found.append(item)
            elif type_ == 'srcs':
                for item in self.hit:
                    if os.path.splitext(item)[-1].lower() in SRC_LIST:
                        self.found.append(item)
            else:
                type_ = '.'+type_
                for item in self.hit:
                    if os.path.splitext(item)[-1].lower()== type_:
                        self.found.append(item)


        else:
            filt = term.rstrip('|')
            for path in self.pathlist:
                if filt.lower() in path.lower():
                    self.found.append(path)
            if self.option !=1:
                for path in self.hiddenlist:
                    if filt.lower() in path.lower():
                        self.found.append(path)

    def SecondarySearch(self,term):
        templist = []
        if len(term.split(' ; ')) > 1 or len(term.split(' , ')) > 1:
            self.status_label.setText('Status: Please have no spaces for delimiters')
        elif len(term.split(';')) > 1:  # and filter
            filt = term.split(';')
            x = 1
            for fil in filt:
                templist2 = []
                if fil != '':
                    if x == 1:
                        for path in self.found:
                            if fil.lower() in path.lower():
                                templist.append(path)
                        x += 1
                    else:
                        for path in templist:
                            if fil.lower() in path.lower():
                                templist2.append(path)
                        templist = []
                        for item in templist2:
                            templist.append(item)
        elif len(term.split(',')) > 1:  # or filter
            filt = term.split(',')
            print(filt)
            for path in self.found:
                for fil in filt:
                    if fil.lower() in path.lower():
                        if path not in templist:
                            templist.append(path)
        else:
            for path in self.found:
                if term.lower() in path.lower():
                    templist.append(path)

        self.found = []
        for item in templist:
            self.found.append(item)

    # still experimenting: only going to do text files
    def DeepSearch(self):
        starttime = time.time()
        if self.deep_line.text() == '' and self.line_edit.text()=='':
            self.resultwindow.listwidget.clear()
            self.status_label.setText('Status: Cleared')
        elif (self.line_edit.text()!='' and len(self.found)>0) and self.deep_line.text()!= '':
            total = len(self.found)
            term = self.deep_line.text()
            self.checkTextFromResult(term,total)
        elif (self.line_edit.text()!='' and len(self.found)==0) and self.deep_line.text()!='':
            self.SearchSplit()
            total = len(self.found)
            term = self.deep_line.text()
            self.checkTextFromResult(term,total)
        elif self.line_edit.text()=='' and self.deep_line.text()!='':
            self.resultwindow.listwidget.clear()
            total = len(self.pathlist) + len(self.hiddenlist)
            count = 0
            self.status_label.setText('Status: Searching...')
            for path in self.pathlist:
                if count%50 == 0:
                    QtGui.QApplication.processEvents()
                count += 1
                self.progress_bar.setValue(int(100 * (count / total)))
                # self.status_label.setText('Status: processing -> ' + path)
                ext = os.path.splitext(path)[-1].lower()
                if ext in EXT_LIST:
                    try:
                        if os.path.isfile(path):
                            f = open(path, 'r')
                            text = f.read()
                            if self.deep_line.text().lower() in text.lower():
                                self.found.append(path)
                                self.resultwindow.updateWidget(path)
                            f.close()
                    except (UnicodeDecodeError, PermissionError) as e:
                        self.error_list.append('error: ' + path)
                # if ext in ['.docx']:
                #     try:
                #         document = docx.Document(path)
                #         templist = []
                #         for paragraph in document.paragraphs:
                #             if self.deep_line.text().lower() in paragraph.text.lower():
                #                 if path not in templist:
                #                     self.resultwindow.listwidget.addItem(path)
                #                     templist.append(path)
                #     except (ValueError, docx.opc.exceptions.PackageNotFoundError) as e:
                #         print(repr(e))
                #         print('error')
            for path in self.hiddenlist:
                    if count%50 == 0:
                        QtGui.QApplication.processEvents()
                    count += 1
                    self.progress_bar.setValue(int(100 * (count / total)))
                    # self.status_label.setText('Status: processing -> ' + path)
                    ext = os.path.splitext(path)[-1].lower()
                    if ext in EXT_LIST:
                        try:
                            if os.path.isfile(path):
                                f = open(path, 'r')
                                text = f.read()
                                if self.deep_line.text().lower() in text.lower():
                                    self.found.append(path)
                                    self.resultwindow.updateWidget(path)
                                f.close()
                        except (UnicodeDecodeError, PermissionError) as e:
                            self.error_list.append('error: ' + path)
                    # if ext in ['.docx']:
                    #     try:
                    #         document = docx.Document(path)
                    #         templist = []
                    #         for paragraph in document.paragraphs:
                    #             if self.deep_line.text().lower() in paragraph.text.lower():
                    #                 if path not in templist:
                    #                     self.resultwindow.listwidget.addItem(path)
                    #                     templist.append(path)
                    #     except (ValueError, docx.opc.exceptions.PackageNotFoundError) as e:
                    #         print(repr(e))
                    #         print('error')

        if self.deep_line.text() !='' and self.resultwindow.listwidget.count()!=0:
            self.resultwindow.updateSize(True)
            self.resultwindow.updateLoc()
            self.resultwindow.show()
            self.resultwindow.activateWindow()

        if (self.deep_line.text() =='' and self.line_edit.text()!='') and self.found!=[]:
            self.resultwindow.listwidget.clear()
            self.resultwindow.updateSize()
            self.resultwindow.updateLoc()
            self.resultwindow.activateWindow()
            self.status_label.setText('Status: Found ' + str(self.resultwindow.listwidget.count()) + ' items' + ' Showing: ' + str(self.resultwindow.listwidget.count()))
        if self.resultwindow.listwidget.count() == 0 and self.deep_line.text()!='':
            self.resultwindow.hide()
            self.status_label.setText('Status: None Found...')
        if self.deep_line.text()!='':
            self.status_label.setText('Status: Found ' + str(self.resultwindow.listwidget.count()) + ' items' + ' Showing: ' + str(self.resultwindow.listwidget.count()))
        endtime = time.time()
        print(endtime - starttime)


    def checkTextFromResult(self,term,total):
        self.resultwindow.listwidget.clear()
        count = 0
        for path in self.found:
                QtGui.QApplication.processEvents()
                count += 1
                self.progress_bar.setValue(int(100 * (count / total)))
                self.status_label.setText('Status: processing ->' + path)
                ext = os.path.splitext(path)[-1].lower()
                if ext in EXT_LIST:
                    try:
                        if os.path.isfile(path):
                            f = open(path, 'r')
                            text = f.read()
                            if term.lower() in text.lower():
                                self.resultwindow.updateWidget(path)
                            f.close()
                    except UnicodeDecodeError:
                        print('error: ' + path)
                        self.error_list.append('error: ' + path)
                # if ext in ['.docx']:
                #     try:
                #         document = docx.Document(path)
                #         templist = []
                #         for paragraph in document.paragraphs:
                #             if term.lower() in paragraph.text.lower():
                #                 if path not in templist:
                #                     self.resultwindow.listwidget.addItem(path)
                #                     templist.append(path)
                #     except ValueError:
                #         print(ValueError)
        self.resultwindow.updateSize(True)
        self.resultwindow.show()


    


    def OpenRestricted(self):
        if sys.platform == 'win32':
            os.startfile(restricted_file)
        else:
            subprocess.call(['xdg-open', restricted_file])


    def ReadArchive(self):
        f = open(path_archive, 'r')
        for line in f:
            self.pathlist.append(line.rstrip('\n'))
        f.close()
        f = open(hidden_path_archive, 'r')
        for line in f:
            self.hiddenlist.append(line.rstrip('\n'))
        self.status_label.setText('Status: Index imported, ready for use!')

    def GenerateArchive(self):
        start = time.time()
        self.status_label.setText('Status: Generating Path Index...')
        self.file_count = 0
        self.dir_count = 0
        self.pathlist = []
        self.hiddenlist = []
        self.hiddendirs = []
        self.restricted_dir = []
        self.error_list = []
        if os.path.isfile(path_archive):
            os.remove(path_archive)
        self.GetSetting()
        self.MainCrawler()
        self.CreateArchive()
        self.CreateRestrictedFolder()
        self.dir_lcd.display(self.dir_count)
        self.file_lcd.display(self.file_count)
        self.status_label.setText('Status: Completed, Index archived and ready for use!')
        end = time.time()
        self.hiddendirs = []
        print(end - start)

    def CreateArchive(self):
        date_time = QtCore.QDateTime().currentDateTime().toString('MM.dd.yyyy - hh:mm:ss AP')
        f = open(path_archive, 'w+')
        x = 0
        for a in self.pathlist:
            try:
                if x ==0:
                    f.write(date_time)
                    f.write('\n')
                    x+=1
                f.write(a)
                f.write("\n")
            except UnicodeEncodeError:
                error = 'couldnt add: ' + a + ' to file'
                self.error_list.append(error)
        f.close()
        f = open(hidden_path_archive, 'w+')
        x = 0
        for a in self.hiddenlist:
            try:
                if x ==0:
                    f.write(date_time)
                    f.write('\n')
                    x+=1
                f.write(a)
                f.write("\n")
            except UnicodeEncodeError:
                error = 'couldnt add: ' + a + ' to file'
                self.error_list.append(error)
        f.close()
        f = open(file_count, 'w+')
        for item in [self.dir_count, self.file_count]:
            f.write(str(item))
            f.write('\n')
        f.close()

    def CreateRestrictedFolder(self):
        f = open(restricted_file, 'w+')
        for item in self.restricted_dir:
            try:
                f.write(item)
                f.write('\n')
            except UnicodeEncodeError:
                print(UnicodeEncodeError)
        f.close()

class MyLineEdit(QtGui.QLineEdit):
    def __init__(self,parent = None):
        super(MyLineEdit,self).__init__(parent)
        self.setStyleSheet("border: 2px solid gray; border-radius: 10px; padding: 0 8px")
        self.parent = parent

    def focusInEvent(self,event):
        self.selectAll()
        if self.parent.resultwindow.isVisible:
            self.parent.resultwindow.raise_()


def main():
    app = QtGui.QApplication(sys.argv)
    search = Searcher()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
