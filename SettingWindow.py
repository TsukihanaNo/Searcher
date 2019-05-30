import os, sys, getpass
from PySide import QtGui, QtCore

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


locations = os.path.join(archivefolder, 'locations.txt')
exception_file = os.path.join(archivefolder, 'exception.txt')
settings = os.path.join(archivefolder,'settings.txt')


class SettingsWindow(QtGui.QWidget):
    def __init__(self, x, y):
        super(SettingsWindow, self).__init__()
        # setting variables
        self.x = x
        self.y = y

        self.date = QtCore.QDate()

        self.tab_widget = QtGui.QTabWidget(self)
        # creating widgets
        self.loc_delete_Button = QtGui.QPushButton('Delete', self)
        self.loc_browse_button = QtGui.QPushButton('Browse', self)

        self.exp_delete_Button = QtGui.QPushButton('Delete', self)
        self.exp_browse_button = QtGui.QPushButton('Browse', self)

        self.save_button = QtGui.QPushButton('Save',self)

        CloseWindowAction = QtGui.QAction(self)
        CloseWindowAction.setShortcut("Ctrl+W")
        CloseWindowAction.triggered.connect(self.close)

        self.addAction(CloseWindowAction)

        self.loc_line_edit = QtGui.QLineEdit(self)
        self.exp_line_edit = QtGui.QLineEdit(self)

        self.timer_time = QtGui.QLineEdit(self)
        self.timer_boot = QtGui.QLineEdit(self)

        self.loc_list_widget = QtGui.QListWidget(self)
        self.exp_list_widget = QtGui.QListWidget(self)

        self.optionlabel = QtGui.QLabel(self)
        self.optionlabel.setText('Option 1: Ignore Hidden Files   (Fastest)\nOption 2: Hidden Files - No Display\nOption 3: Hidden Files - Display')
        self.option = QtGui.QLineEdit(self)

        if os.path.isfile(exception_file):
            f = open(exception_file, 'r')
            for line in f:
                self.exp_list_widget.addItem(line.rstrip('\n'))
            f.close()
        if os.path.isfile(locations):
            f = open(locations, 'r')
            for line in f:
                self.loc_list_widget.addItem(line.rstrip('\n'))
            f.close()
        self.readSettings()

        self.initUI()


    def initUI(self):
        # layouts and setup
        hlayout = QtGui.QHBoxLayout(self)
        self.CreateLocationTab()
        hlayout.addWidget(self.tab_widget)
        hlayout.setContentsMargins(0, 0, 0, 0)

        # widget settings
        self.loc_list_widget.setSelectionMode(QtGui.QListWidget.ExtendedSelection)
        self.exp_list_widget.setSelectionMode(QtGui.QListWidget.ExtendedSelection)

        # connecting signals
        self.loc_line_edit.returnPressed.connect(self.AddToLocList)
        self.loc_line_edit.returnPressed.connect(self.SaveLocLocation)
        self.loc_browse_button.clicked.connect(self.GetLocDirectory)
        self.loc_delete_Button.clicked.connect(self.DeleteLocItem)

        self.exp_line_edit.returnPressed.connect(self.AddToExpList)
        self.exp_line_edit.returnPressed.connect(self.SaveExpLocation)
        self.exp_browse_button.clicked.connect(self.GetExpDirectory)
        self.exp_delete_Button.clicked.connect(self.DeleteExpItem)

        self.loc_list_widget.doubleClicked.connect(self.DeleteLocItem)
        self.exp_list_widget.doubleClicked.connect(self.DeleteExpItem)

        self.save_button.clicked.connect(self.SaveSettings)

        self.CreateActions()

        # window settings
        self.setGeometry(self.x, self.y, 300, 300)
        self.setWindowTitle("Settings")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.show()


    def CreateLocationTab(self):
        vlayout1 = QtGui.QVBoxLayout(self)
        vlayout2 = QtGui.QVBoxLayout(self)
        vlayout4 = QtGui.QVBoxLayout(self)
        hlayout1 = QtGui.QHBoxLayout(self)
        hlayout2 = QtGui.QHBoxLayout(self)

        hlayout3 = QtGui.QHBoxLayout(self)
        vlayout = QtGui.QVBoxLayout(self)

        groupbox1 = QtGui.QGroupBox('Search Locations', self)
        groupbox2 = QtGui.QGroupBox('Excluded Locations', self)
        groupbox3 = QtGui.QGroupBox('Update Settings',self)
        groupbox4 = QtGui.QGroupBox('Generate and Search Settings',self)

        # adding widgets to layouts
        hlayout1.addWidget(self.loc_line_edit)
        hlayout1.addWidget(self.loc_browse_button)
        hlayout1.addWidget(self.loc_delete_Button)

        hlayout2.addWidget(self.exp_line_edit)
        hlayout2.addWidget(self.exp_browse_button)
        hlayout2.addWidget(self.exp_delete_Button)

        v1 = QtGui.QVBoxLayout()
        v2 = QtGui.QVBoxLayout()

        v1.addWidget(QtGui.QLabel('Update Rate (ms, 0 is off)'))
        v1.addWidget(self.timer_time)
        v2.addWidget(QtGui.QLabel('Update on Start (on/off)'))
        v2.addWidget(self.timer_boot)

        hlayout3.addLayout(v1)
        hlayout3.addLayout(v2)

        vlayout.addWidget(self.optionlabel)
        vlayout.addWidget(self.option)

        vlayout1.addLayout(hlayout1)
        vlayout1.addWidget(self.loc_list_widget)
        groupbox1.setLayout(vlayout1)
        vlayout2.addLayout(hlayout2)
        vlayout2.addWidget(self.exp_list_widget)
        groupbox2.setLayout(vlayout2)
        groupbox3.setLayout(hlayout3)

        groupbox4.setLayout(vlayout)

        vlayout4.addWidget(groupbox1)
        vlayout4.addWidget(groupbox2)
        vlayout4.addWidget(groupbox3)
        vlayout4.addWidget(groupbox4)

        vlayout4.addWidget(self.save_button)

        location_widget = QtGui.QWidget()
        location_widget.setLayout(vlayout4)

        self.tab_widget.addTab(location_widget, ' Search Locations')

    def CreateActions(self):
        Close1 = QtGui.QAction(self)
        Close1.setShortcut('Ctrl+Q')
        Close1.triggered.connect(self.close)

        self.addAction(Close1)


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def mousePressEvent(self,event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if event.pos().x() < self.size().width() -20:
                self.diff = event.globalPos() - self.frameGeometry().topLeft()
                self.mode = 'drag'
            else:
                self.mode = 'resize'


    def mouseMoveEvent(self,event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.mode == 'drag':
                self.move(event.globalPos()-self.diff)
            else:
                self.resize(event.pos().x(),event.pos().y())

    def GetLocDirectory(self):
        file_dialog = QtGui.QFileDialog(self)
        directory = file_dialog.getExistingDirectory()
        self.loc_list_widget.addItem(directory)
        self.SaveLocLocation()

    def AddToLocList(self):
        self.loc_list_widget.addItem(self.loc_line_edit.text())
        self.loc_line_edit.clear()

    def DeleteLocItem(self):
        for item in self.loc_list_widget.selectedItems():
            self.loc_list_widget.takeItem(self.loc_list_widget.row(item))
        self.SaveLocLocation()

    def SaveLocLocation(self):
        f = open(locations, 'w+')
        for x in range(self.loc_list_widget.count()):
            f.write(self.loc_list_widget.item(x).text())
            f.write('\n')
        f.close()

    def GetExpDirectory(self):
        file_dialog = QtGui.QFileDialog(self)
        directory = file_dialog.getExistingDirectory()
        self.exp_list_widget.addItem(directory)
        self.SaveExpLocation()

    def AddToExpList(self):
        self.exp_list_widget.addItem(self.exp_line_edit.text())
        self.exp_line_edit.clear()

    def DeleteExpItem(self):
        for item in self.exp_list_widget.selectedItems():
            self.exp_list_widget.takeItem(self.exp_list_widget.row(item))
        self.SaveExpLocation()

    def SaveExpLocation(self):
        f = open(exception_file, 'w+')
        for x in range(self.exp_list_widget.count()):
            f.write(self.exp_list_widget.item(x).text())
            f.write('\n')
        f.close()

    def SaveSettings(self):
        f = open(settings,'w+')
        if self.timer_time.text() != '':
            f.write(self.timer_time.text())
        else:
            f.write('0')
        f.write('\n')
        if self.timer_boot.text()!='':
            f.write(self.timer_boot.text())
        else:
            f.write('off')
        f.write('\n')
        if self.option.text() !='':
            f.write(self.option.text())
        else:
            f.write('1')
        f.close()

    def readSettings(self):
        if os.path.isfile(settings):
            f = open(settings,'r')
            x=0
            for line in f:
                if x == 0:
                    self.timer_time.setText(line.rstrip('\n'))
                    x+=1
                elif x ==1:
                    self.timer_boot.setText(line.rstrip('\n'))
                    x+=1
                else:
                    self.option.setText(line.rstrip('\n'))


def main():
    app = QtGui.QApplication(sys.argv)
    setting = SettingsWindow(100,100)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
