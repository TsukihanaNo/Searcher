from PySide import QtGui, QtCore, QtWebKit
import pygal, os, sys

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))

monitor_archive = os.path.join(program_location, 'monitor archive')
if not os.path.isdir(monitor_archive):
    os.mkdir(monitor_archive)
graphs = os.path.join(monitor_archive, 'graphs')
if not os.path.isdir(graphs):
    os.mkdir(graphs)
line_all_svg = os.path.join(graphs, 'allline.svg')
line_size_svg = os.path.join(graphs, 'sizeline.svg')
line_filecount_svg = os.path.join(graphs, 'filecountline.svg')
line_foldercount_svg = os.path.join(graphs, 'foldercountline.svg')

icon = os.path.join(program_location, 'find.png')


class MonitorGraph(QtGui.QWidget):
    def __init__(self):
        super(MonitorGraph, self).__init__()
        self.filemodel = QtGui.QFileSystemModel()
        self.fileview = QtGui.QTreeView(self)
        self.web_view1 = QtWebKit.QWebView(self)
        self.web_view2 = QtWebKit.QWebView(self)
        self.web_view3 = QtWebKit.QWebView(self)
        self.web_view4 = QtWebKit.QWebView(self)
        self.tab_widget = QtGui.QTabWidget(self)
        self.initUI()


    def initUI(self):
        self.createActions()
        self.fileview.setModel(self.filemodel)
        self.fileview.hideColumn(1)
        self.fileview.hideColumn(2)
        self.fileview.hideColumn(3)
        self.fileview.setRootIndex(self.filemodel.setRootPath(monitor_archive))
        self.fileview.setSelectionMode(QtGui.QTreeView.ExtendedSelection)
        self.fileview.clicked.connect(self.clicked)
        self.fileview.setMinimumWidth(150)
        splitter = QtGui.QSplitter(self)
        splitter.addWidget(self.fileview)
        splitter.addWidget(self.tab_widget)
        splitter.setStretchFactor(0, 4)

        self.tab_widget.addTab(self.web_view1, 'all')
        self.tab_widget.addTab(self.web_view2, 'size')
        self.tab_widget.addTab(self.web_view3, 'file count')
        self.tab_widget.addTab(self.web_view4, 'folder count')

        hlayout = QtGui.QHBoxLayout(self)
        hlayout.addWidget(splitter)
        self.setWindowTitle("Archive Monitor")
        self.setGeometry(100, 100, 1000, 600)
        ico = QtGui.QIcon(icon)
        self.setWindowIcon(ico)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.dispCurrentMonth()


    def dispCurrentMonth(self):
        date = QtCore.QDate()
        date1 = date.currentDate().toString('MM.dd.yyyy').split('.')
        filename = date1[0] + '.' + date1[2] + '.csv'
        path = os.path.join(monitor_archive, filename)
        if os.path.isfile(path):
            data = self.readData(path)
            self.plotData(data)
            self.displayPlot()


    def clicked(self):
        index = self.fileview.selectionModel().currentIndex()
        path = self.filemodel.filePath(index)
        data = self.readData(path)
        self.plotData(data)
        self.displayPlot()

    def readData(self, path):
        f = open(path, 'r')
        data = []
        for line in f:
            data.append(line)
        return data

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def delete(self):
        indices = self.fileview.selectionModel().selectedIndexes()
        paths = []
        for index in indices:
            paths.append(self.filemodel.filePath(index))
        try:
            for item in paths:
                os.remove(item)
        except:
            print('couldnt delete file: ' + item)

    def createActions(self):
        Close1 = QtGui.QAction(self)
        Close1.setShortcut('Ctrl+W')
        Close1.triggered.connect(self.close)
        self.addAction(Close1)
        Close2 = QtGui.QAction(self)
        Close2.setShortcut('Ctrl+Q')
        Close2.triggered.connect(self.close)
        self.addAction(Close2)

        deleteAction = QtGui.QAction('delete', self)
        deleteAction.triggered.connect(self.delete)

        self.fileview.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.fileview.addAction(deleteAction)

    def plotData(self, data):
        date = []
        filecount = []
        foldercount = []
        size = []
        x = 0
        for item in data:
            if x > 0:
                values = item.split(',')
                print(values)
                date.append((values[0]))
                size.append(float(values[1]))
                filecount.append(int(values[2]))
                foldercount.append(int(values[3].rstrip('\n')))
            x += 1
        self.allGraph(date, size, filecount, foldercount)
        self.sizeGraph(date, size)
        self.filecountGraph(date, filecount)
        self.foldercountGraph(date, foldercount)
        self.displayPlot()


    def allGraph(self, date, size, filecount, foldercount):
        plot = pygal.Line()
        plot.title = 'archive changes'
        plot.x_labels = date
        plot.add('size', size)
        plot.add('file count', filecount)
        plot.add('folder count', foldercount)
        plot.render_to_file(line_all_svg)

    def sizeGraph(self, date, size):
        plot = pygal.Line()
        plot.title = 'size change'
        plot.x_labels = date
        plot.add('total size', size)
        plot.render_to_file(line_size_svg)

    def filecountGraph(self, date, filecount):
        plot = pygal.Line()
        plot.title = 'file count change'
        plot.x_labels = date
        plot.add('filecount', filecount)
        plot.render_to_file(line_filecount_svg)

    def foldercountGraph(self, date, foldercount):
        plot = pygal.Line()
        plot.title = 'folder count change'
        plot.x_labels = date
        plot.add('folder count', foldercount)
        plot.render_to_file(line_foldercount_svg)

    def displayPlot(self):
        self.web_view1.load(line_all_svg)
        self.web_view2.load(line_size_svg)
        self.web_view3.load(line_filecount_svg)
        self.web_view4.load(line_foldercount_svg)



