import os, sys
from PySide import QtGui, QtCore

if getattr(sys, 'frozen', False):
    # frozen
    program_location = os.path.dirname(sys.executable)
else:
    # unfrozen
    program_location = os.path.dirname(os.path.realpath(__file__))


class InfoWindow(QtGui.QWidget):
    def __init__(self, x, y):
        super(InfoWindow, self).__init__()
        # variables
        self.x = x
        self.y = y

        # creating widgets
        self.textedit = QtGui.QTextEdit(self)

        CloseWindowAction = QtGui.QAction(self)
        CloseWindowAction.setShortcut("Ctrl+W")
        CloseWindowAction.triggered.connect(self.close)

        CloseWindowAction2 = QtGui.QAction(self)
        CloseWindowAction2.setShortcut("Ctrl+Q")
        CloseWindowAction2.triggered.connect(self.close)

        self.addAction(CloseWindowAction)
        self.addAction(CloseWindowAction2)

        self.initUI()

    def initUI(self):
        # layouts
        vlayout = QtGui.QVBoxLayout(self)
        vlayout.addWidget(self.textedit)
        vlayout.setContentsMargins(0,0,0,0)

        # window settings
        self.setGeometry(self.x, self.y, 400, 400)
        self.setWindowTitle('Information Log')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

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

