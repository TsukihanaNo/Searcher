import os, sys
from PySide import QtGui, QtCore, QtWebKit
from pygal import Bar, HorizontalBar, Pie

if sys.platform == 'win32':
    import win32security
else:
    import pwd, grp

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

graphfolder = os.path.join(program_location, 'graphs')
if not os.path.isdir(graphfolder):
    os.mkdir(os.path.join(program_location, 'graphs'))

piesvg = os.path.join(program_location, graphfolder, 'diskpie.svg')
horisvg = os.path.join(program_location, graphfolder, 'diskhori.svg')
countpiesvg = os.path.join(program_location, graphfolder, 'diskcountpie.svg')
counthorisvg = os.path.join(program_location, graphfolder, 'diskcounthori.svg')
foldercountpiesvg = os.path.join(program_location, graphfolder, 'diskfoldercountpie.svg')
foldercounthorisvg = os.path.join(program_location, graphfolder, 'diskfoldercounthori.svg')
vertsvg = os.path.join(program_location, graphfolder, 'diskvert.svg')
vertcounthorisvg = os.path.join(program_location, graphfolder, 'diskcountvert.svg')
vertfoldercounthorisvg = os.path.join(program_location, graphfolder, 'diskfoldercountvert.svg')
gif = os.path.join(program_location, 'giff.gif')
icon = os.path.join(program_location, 'find.png')


class DiskReport(QtGui.QWidget):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        super(DiskReport, self).__init__()
        self.dir_model = QtGui.QFileSystemModel()
        self.folder_view = QtGui.QTreeView(self)
        self.text = QtGui.QTextEdit(self)
        self.web = QtWebKit.QWebView(self)
        self.web2 = QtWebKit.QWebView(self)
        self.web3 = QtWebKit.QWebView(self)
        self.tab_widget = QtGui.QTabWidget(self)
        self.toolbar = QtGui.QToolBar(self)
        self.tree = []

        self.showpie = True
        self.showhori = False
        self.showvert = False

        self.initUI()

    def initUI(self):
        self.CreateActions()
        self.dir_model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.folder_view.setModel(self.dir_model)
        self.folder_view.clicked.connect(self.clicked)
        self.folder_view.setHeaderHidden(True)
        self.folder_view.hideColumn(1)
        self.folder_view.hideColumn(2)
        self.folder_view.hideColumn(3)
        self.folder_view.expanded.connect(self.UpdateScroll)
        self.folder_view.collapsed.connect(self.UpdateScroll)

        self.folder_view.setMinimumWidth(150)
        # tab widget setup
        self.tab_widget.addTab(self.web, 'By Folder Size')
        self.tab_widget.addTab(self.web2, 'By File Count')
        self.tab_widget.addTab(self.web3, 'By Folder Count')

        splitter = QtGui.QSplitter(self)

        splitter2 = QtGui.QSplitter(self)
        splitter2.addWidget(self.toolbar)
        splitter2.addWidget(self.tab_widget)
        splitter2.addWidget(self.text)
        splitter2.setOrientation(QtCore.Qt.Vertical)

        splitter.addWidget(self.folder_view)
        splitter.addWidget(splitter2)

        self.tab_widget.currentChanged.connect(self.DisplayText)

        hlayoutbox = QtGui.QHBoxLayout(self)
        hlayoutbox.addWidget(splitter)
        self.setLayout(hlayoutbox)

        self.dir_model.setRootPath('')
        self.setWindowTitle("Disk Report")
        self.setGeometry(self.x + 650, self.y + 30, 850, 700)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        ico = QtGui.QIcon(icon)
        self.setWindowIcon(ico)

    def UpdateScroll(self):
        self.folder_view.resizeColumnToContents(0)

    def loading(self):
        self.web.load(gif)
        self.web2.load(gif)
        self.web3.load(gif)

    def clicked(self):
        self.loading()
        index = self.folder_view.selectionModel().currentIndex()
        dir_path = self.dir_model.filePath(index)
        self.foldersize = 0
        self.totalcount = 0
        self.filesize = 0
        self.filecount = 0
        self.totalfolders = 0
        self.text.clear()
        self.tree.clear()
        self.text.append('Processing Data...')
        for filename in os.listdir(dir_path):
            path = os.path.join(dir_path, filename)
            if os.path.isdir(path):
                if sys.platform == 'win32':
                    sd = win32security.GetFileSecurity(path, win32security.OWNER_SECURITY_INFORMATION)
                    owner_sid = sd.GetSecurityDescriptorOwner()
                    user, group, sid_type = win32security.LookupAccountSid(None, owner_sid)
                else:
                    stat = os.stat(path)
                    uid = stat.st_uid
                    gid = stat.st_gid
                    user = pwd.getpwuid(uid)[0]
                    group = grp.getgrgid(gid)[0]

                self.totalsize = 0
                self.count = 0
                self.foldercount = 0
                self.Crawler(path)
                self.tree.append((path.split('\\')[-1], self.totalsize, self.count, self.foldercount, user, group))
                self.foldersize += self.totalsize
                self.totalcount += self.count
                self.totalfolders += self.foldercount
            else:
                self.filesize += os.path.getsize(path)
                self.filecount += 1
                self.totalcount += self.filecount
        self.foldersize += self.filesize
        self.foldersize = self.foldersize / (1024 * 1024)
        self.filesize = self.filesize / (1024 * 1024)
        self.DisplayText()
        if self.showpie:
            self.PieDisplaySizeGraph()
            self.PieDisplayFileCountGraph()
            self.PieDisplayFolderCountGraph()
        elif self.showhori:
            self.BarDisplaySizeGraph()
            self.BarDisplayFileCountGraph()
            self.BarDisplayFolderCountGraph()
        else:
            self.VerBarDisplaySizeGraph()
            self.VerBarDisplayFileCountGraph()
            self.VerBarDisplayFolderCountGraph()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def CreateActions(self):
        Close1 = QtGui.QAction(self)
        Close1.setShortcut('Ctrl+W')
        Close1.triggered.connect(self.close)
        self.addAction(Close1)
        Close2 = QtGui.QAction(self)
        Close2.setShortcut('Ctrl+Q')
        Close2.triggered.connect(self.close)
        self.addAction(Close2)

        showpie = QtGui.QAction('Pie', self)
        showpie.triggered.connect(self.ShowPie)

        showhori = QtGui.QAction('Hori', self)
        showhori.triggered.connect(self.ShowHori)

        showvert = QtGui.QAction('Vert', self)
        showvert.triggered.connect(self.ShowVert)

        self.toolbar.addAction(showpie)
        self.toolbar.addAction(showhori)
        self.toolbar.addAction(showvert)

    def ShowPie(self):
        self.showpie = True
        self.showhori = False
        self.showvert = False
        self.PieDisplaySizeGraph()
        self.PieDisplayFileCountGraph()
        self.PieDisplayFolderCountGraph()

    def ShowHori(self):
        self.showpie = False
        self.showhori = True
        self.showvert = False
        self.BarDisplaySizeGraph()
        self.BarDisplayFileCountGraph()
        self.BarDisplayFolderCountGraph()


    def ShowVert(self):
        self.showpie = False
        self.showhori = False
        self.showvert = True
        self.VerBarDisplaySizeGraph()
        self.VerBarDisplayFileCountGraph()
        self.VerBarDisplayFolderCountGraph()

    def Crawler(self, folder):
        try:
            for item in os.listdir(folder):
                QtGui.QApplication.processEvents()
                path = os.path.join(folder, item)
                if not os.path.isdir(path):
                    self.count += 1
                    self.totalsize += os.path.getsize(path)
                else:
                    self.foldercount += 1
                    self.Crawler(path)
        except:
            print('error')


    def PieDisplaySizeGraph(self):
        self.SortBySize()
        piechart = Pie()
        piechart.title = 'Folder Usages by total size'
        if len(self.tree) >= 5:
            piechart.add(self.tree[0][0], 100 * self.tree[0][1] / self.foldersize)
            piechart.add(self.tree[1][0], 100 * self.tree[1][1] / self.foldersize)
            piechart.add(self.tree[2][0], 100 * self.tree[2][1] / self.foldersize)
            piechart.add(self.tree[3][0], 100 * self.tree[3][1] / self.foldersize)
            piechart.add(self.tree[4][0], 100 * self.tree[4][1] / self.foldersize)
        else:
            for item in self.tree:
                piechart.add(item[0], 100 * item[1] / self.foldersize)
        piechart.add('Unsorted Files', 100 * self.filesize / self.foldersize)
        piechart.render_to_file(piesvg)
        self.web.load(piesvg)

    def BarDisplaySizeGraph(self):
        self.SortBySize()
        horizontal = HorizontalBar()
        horizontal.title = 'Folder Usage by total size '
        if len(self.tree) >= 5:
            horizontal.add(self.tree[0][0], self.tree[0][1] / (1024 * 1024))
            horizontal.add(self.tree[1][0], self.tree[1][1] / (1024 * 1024))
            horizontal.add(self.tree[2][0], self.tree[2][1] / (1024 * 1024))
            horizontal.add(self.tree[3][0], self.tree[3][1] / (1024 * 1024))
            horizontal.add(self.tree[4][0], self.tree[4][1] / (1024 * 1024))
        else:
            for item in self.tree:
                horizontal.add(item[0], item[1] / (1024 * 1024))
        horizontal.add('Unsorted Files', self.filesize)
        horizontal.render_to_file(horisvg)
        self.web.load(horisvg)

    def VerBarDisplaySizeGraph(self):
        self.SortBySize()
        bar = Bar()
        bar.title = 'Folder Usage by total size '
        if len(self.tree) >= 5:
            bar.add(self.tree[0][0], self.tree[0][1] / (1024 * 1024))
            bar.add(self.tree[1][0], self.tree[1][1] / (1024 * 1024))
            bar.add(self.tree[2][0], self.tree[2][1] / (1024 * 1024))
            bar.add(self.tree[3][0], self.tree[3][1] / (1024 * 1024))
            bar.add(self.tree[4][0], self.tree[4][1] / (1024 * 1024))
        else:
            for item in self.tree:
                bar.add(item[0], item[1] / (1024 * 1024))
        bar.add('Unsorted Files', self.filesize)
        bar.render_to_file(vertsvg)
        self.web.load(vertsvg)


    def PieDisplayFileCountGraph(self):
        self.SortByFileCount()
        piechart = Pie()
        piechart.title = 'Folder Usages by File Count'
        if len(self.tree) >= 5:
            piechart.add(self.tree[0][0], 100 * self.tree[0][2] / self.totalcount)
            piechart.add(self.tree[1][0], 100 * self.tree[1][2] / self.totalcount)
            piechart.add(self.tree[2][0], 100 * self.tree[2][2] / self.totalcount)
            piechart.add(self.tree[3][0], 100 * self.tree[3][2] / self.totalcount)
            piechart.add(self.tree[4][0], 100 * self.tree[4][2] / self.totalcount)
        else:
            for item in self.tree:
                piechart.add(item[0], 100 * item[2] / self.totalcount)
        piechart.add('Unsorted Files', 100 * self.filecount / self.totalcount)
        piechart.render_to_file(countpiesvg)
        self.web2.load(countpiesvg)

    def BarDisplayFileCountGraph(self):
        self.SortByFileCount()
        horizontal = HorizontalBar()
        horizontal.title = 'Folder Usage by File Count '
        if len(self.tree) >= 5:
            horizontal.add(self.tree[0][0], self.tree[0][2])
            horizontal.add(self.tree[1][0], self.tree[1][2])
            horizontal.add(self.tree[2][0], self.tree[2][2])
            horizontal.add(self.tree[3][0], self.tree[3][2])
            horizontal.add(self.tree[4][0], self.tree[4][2])
        else:
            for item in self.tree:
                horizontal.add(item[0], item[2])
        horizontal.add('Unsorted Files', self.filecount)
        horizontal.render_to_file(counthorisvg)
        self.web2.load(counthorisvg)

    def VerBarDisplayFileCountGraph(self):
        self.SortByFileCount()
        bar = Bar()
        bar.title = 'Folder Usage by File Count '
        if len(self.tree) >= 5:
            bar.add(self.tree[0][0], self.tree[0][2])
            bar.add(self.tree[1][0], self.tree[1][2])
            bar.add(self.tree[2][0], self.tree[2][2])
            bar.add(self.tree[3][0], self.tree[3][2])
            bar.add(self.tree[4][0], self.tree[4][2])
        else:
            for item in self.tree:
                bar.add(item[0], item[2])
        bar.add('Unsorted Files', self.filecount)
        bar.render_to_file(vertcounthorisvg)
        self.web2.load(vertcounthorisvg)

    def PieDisplayFolderCountGraph(self):
        self.SortByFolderCount()
        piechart = Pie()
        piechart.title = 'Folder Usages by File Count'
        if len(self.tree) >= 5:
            piechart.add(self.tree[0][0], 100 * self.tree[0][3] / self.totalfolders)
            piechart.add(self.tree[1][0], 100 * self.tree[1][3] / self.totalfolders)
            piechart.add(self.tree[2][0], 100 * self.tree[2][3] / self.totalfolders)
            piechart.add(self.tree[3][0], 100 * self.tree[3][3] / self.totalfolders)
            piechart.add(self.tree[4][0], 100 * self.tree[4][3] / self.totalfolders)
        else:
            for item in self.tree:
                piechart.add(item[0], 100 * item[3] / self.totalfolders)
        piechart.render_to_file(foldercountpiesvg)
        self.web3.load(foldercountpiesvg)


    def BarDisplayFolderCountGraph(self):
        self.SortByFolderCount()
        horizontal = HorizontalBar()
        horizontal.title = 'Folder Usage by Folder Count '
        if len(self.tree) >= 5:
            horizontal.add(self.tree[0][0], self.tree[0][3])
            horizontal.add(self.tree[1][0], self.tree[1][3])
            horizontal.add(self.tree[2][0], self.tree[2][3])
            horizontal.add(self.tree[3][0], self.tree[3][3])
            horizontal.add(self.tree[4][0], self.tree[4][3])
        else:
            for item in self.tree:
                horizontal.add(item[0], item[3])
        horizontal.render_to_file(vertfoldercounthorisvg)
        self.web3.load(vertfoldercounthorisvg)


    def VerBarDisplayFolderCountGraph(self):
        self.SortByFolderCount()
        bar = Bar()
        bar.title = 'Folder Usage by Folder Count '
        if len(self.tree) >= 5:
            bar.add(self.tree[0][0], self.tree[0][3])
            bar.add(self.tree[1][0], self.tree[1][3])
            bar.add(self.tree[2][0], self.tree[2][3])
            bar.add(self.tree[3][0], self.tree[3][3])
            bar.add(self.tree[4][0], self.tree[4][3])
        else:
            for item in self.tree:
                bar.add(item[0], item[3])
        bar.render_to_file(foldercounthorisvg)
        self.web3.load(foldercounthorisvg)


    def DisplayText(self):
        self.text.clear()
        if self.tab_widget.currentIndex() == 0:
            self.SortBySize()
        elif self.tab_widget.currentIndex() == 1:
            self.SortByFileCount()
        else:
            self.SortByFolderCount()
        self.text.append('Folder Total Size: ' + str(self.foldersize) + 'MB')
        self.text.append('Total File Count: ' + str(self.totalcount))
        self.text.append('')
        x = 1
        for item in self.tree:
            self.text.append(str(x) + ':')
            self.text.append('folder: ' + item[0])
            self.text.append('folder count: ' + str(item[3]))
            self.text.append('size: ' + str((item[1] / (1024 * 1024))) + 'MB')
            self.text.append('file count: ' + str(item[2]))
            self.text.append('owner: ' + item[4])
            self.text.append('group: ' + item[5])
            self.text.append('')
            x += 1
        self.text.append('uncategorized files:')
        self.text.append('size: ' + str(self.filesize) + 'MB')
        self.text.append('count: ' + str(self.filecount))
        self.text.moveCursor(QtGui.QTextCursor.Start)

    def SortBySize(self):
        self.tree = sorted(self.tree, key=lambda tree: tree[1], reverse=True)

    def SortByFileCount(self):
        self.tree = sorted(self.tree, key=lambda tree: tree[2], reverse=True)

    def SortByFolderCount(self):
        self.tree = sorted(self.tree, key=lambda tree: tree[3], reverse=True)


