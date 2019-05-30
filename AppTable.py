from PySide import QtGui,QtCore
import os


class AppTable(QtGui.QWidget):
	def __init__(self):
		super(AppTable, self).__init__()
		self.table = QtGui.QTableWidget(self)
		self.initUI()

	def initUI(self):
		vlayout = QtGui.QVBoxLayout(self)
		vlayout.addWidget(self.table)

		applist = []
		for item in os.listdir(r'/usr/share/applications'):
			applist.append(item.split('.')[0])
		self.table.setRowCount(len(applist))
		self.table.setColumnCount(1)

		x=-1
		for item in applist:
			table_item = QtGui.QTableWidgetItem(item)
			self.table.setItem(x,1,table_item)
			x+=1

		self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

		self.setGeometry(100, 100, 350, 450)
		self.setWindowTitle('App Table')
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

	def createActions(self):
	    Close1 = QtGui.QAction(self)
	    Close1.setShortcut('Ctrl+W')
	    Close1.triggered.connect(self.close)
	    self.addAction(Close1)
	    Close2 = QtGui.QAction(self)
	    Close2.setShortcut('Ctrl+Q')
	    Close2.triggered.connect(self.close)
	    self.addAction(Close2)

