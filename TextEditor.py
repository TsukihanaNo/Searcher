from PySide import QtGui, QtCore


class TextEditor(QtGui.QWidget):
    def __init__(self):
        super(TextEditor, self).__init__()
        self.textedit = QtGui.QTextEdit(self)
        self.menubar = QtGui.QMenuBar(self)
        self.initUI()

    def initUI(self):
        self.createActions()
        vlayout = QtGui.QVBoxLayout(self)
        vlayout.addWidget(self.textedit)

        vlayout.setMenuBar(self.menubar)

        self.setWindowTitle('Text Editor')
        self.setGeometry(100, 100, 500, 600)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def createActions(self):
        filemenu = self.menubar.addMenu('&File')

        openFileAction = QtGui.QAction('&Open File', self)
        openFileAction.setShortcut("Ctrl+O")
        openFileAction.triggered.connect(self.openFile)

        saveFileAction = QtGui.QAction('&Save File', self)
        saveFileAction.setShortcut("Ctrl+S")
        saveFileAction.triggered.connect(self.saveFile)

        FindAction = QtGui.QAction('&Find', self)
        FindAction.setShortcut('Ctrl+F')
        FindAction.triggered.connect(self.findAll)

        ResetHighlightAction = QtGui.QAction('&Reset Highlight',self)
        ResetHighlightAction.setShortcut('Ctrl+R')
        ResetHighlightAction.triggered.connect(self.resetHighlight)

        filemenu.addAction(openFileAction)
        filemenu.addAction(saveFileAction)
        filemenu.addSeparator()
        filemenu.addAction(FindAction)
        filemenu.addAction(ResetHighlightAction)


    def openFile(self):
        file_dialog = QtGui.QFileDialog(self)
        path = file_dialog.getOpenFileName()[0]
        f = open(path, 'r')
        self.textedit.append(f.read())
        f.close()

    def saveFile(self):
        file_dialog = QtGui.QFileDialog(self)
        path = file_dialog.getSaveFileName()[0]
        f = open(path, 'w+')
        try:
            f.write(self.textedit.toPlainText())
            f.close()
        except:
            print('error saving file')

    def findAll(self):
        text,okay = QtGui.QInputDialog.getText(self, '&Find','Enter Search pattern')

        if okay:
            self.resetHighlight()
            self.highlight(text)

    def highlight(self, term):
        extra_selections = []
        self.textedit.moveCursor(QtGui.QTextCursor.Start)
        while (self.textedit.find(term)):
            extra = QtGui.QTextEdit.ExtraSelection()
            extra.format.setBackground(QtGui.QColor(QtCore.Qt.blue).lighter(150))
            extra.cursor = self.textedit.textCursor()
            extra_selections.append(extra)

        self.textedit.setExtraSelections(extra_selections)

    def resetHighlight(self):
        extra_selections = []
        self.textedit.setExtraSelections(extra_selections)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
