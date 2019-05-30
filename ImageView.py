from PySide import QtGui, QtCore
import sys, os

class ImageView(QtGui.QWidget):
	def __init__(self,imagelist,parent = None):
		super(ImageView,self).__init__(parent)
		self.imagesize = None
		self.mode = ''
		self.imageList = imagelist[0]
		self.index = imagelist[1]
		self.title_label = QtGui.QLabel(self)
		self.imagesizelabel = QtGui.QLabel(self)
		self.cursizelabel = QtGui.QLabel(self)
		self.image_label = QtGui.QLabel(self)
		self.image_label.setBackgroundRole(QtGui.QPalette.Base)
		self.image_label.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Ignored)
		self.image_label.setScaledContents(True)
		self.installEventFilter(self)

		CloseWindowAction = QtGui.QAction(self)
		CloseWindowAction.setShortcut("Ctrl+W")
		CloseWindowAction.triggered.connect(self.close)

		self.addAction(CloseWindowAction)


		self.scrollarea = QtGui.QScrollArea(self)
		self.scrollarea.setBackgroundRole(QtGui.QPalette.Dark)
		self.scrollarea.setWidget(self.image_label)

		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(self.imagesizelabel)
		hbox.addWidget(self.title_label)
		hbox.addWidget(self.cursizelabel)
		hbox.setContentsMargins(3,0,3,0)

		qbox = QtGui.QVBoxLayout(self)
		qbox.addLayout(hbox)
		qbox.addWidget(self.scrollarea)
		qbox.setContentsMargins(0,5,0,0)

		info = QtCore.QFileInfo(self.imageList[self.index])
		self.title_label.setText(info.fileName())
		self.title_label.setAlignment(QtCore.Qt.AlignCenter)
		self.imagesizelabel.setAlignment(QtCore.Qt.AlignLeft)
		self.cursizelabel.setAlignment(QtCore.Qt.AlignRight)

		self.setMinimumHeight(10)
		self.setMinimumWidth(10)
		
		self.setWindowTitle('Image Viewer')
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setGeometry(10,10,500,400)
		if self.index ==0:
			self.open(self.imageList[0])
		self.show()


	def open(self,image_path):
		if image_path:
			image = QtGui.QImage(image_path)
			if image.isNull():
				QtGui.QMessageBox.information(self,"Image View","Cannot load %s." %image_path)
				return
			self.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
			self.scrollarea.setWidgetResizable(True)
			self.imagesize = image.size()
			self.updateTitle()
			

	def eventFilter(self,object,event):
		if event.type() == QtCore.QEvent.KeyRelease:
			if event.key() == QtCore.Qt.Key_Left:
				if self.index ==0: self.index = len(self.imageList)
				self.index-=1
				self.open(self.imageList[self.index])
			if event.key() == QtCore.Qt.Key_Right:
				if self.index>=len(self.imageList)-1: self.index =0
				self.index+=1
				self.open(self.imageList[self.index])
			if event.key() == QtCore.Qt.Key_W:
				self.resize(500,400)
			if event.key() == QtCore.Qt.Key_R:
				if self.imagesize.height() > QtGui.QDesktopWidget().availableGeometry().height():
					ratio = QtGui.QDesktopWidget().availableGeometry().height() / self.imagesize.height()
					self.resize(int(self.imagesize.width()*ratio),int(self.imagesize.height()*ratio))
				else:	
					self.resize(self.imagesize.width(),self.imagesize.height())
			if event.key() == QtCore.Qt.Key_E:
				self.move(self.pos().x(),0)
				ratio = QtGui.QDesktopWidget().availableGeometry().height() / self.imagesize.height()
				self.resize(int(self.imagesize.width()*ratio),int(self.imagesize.height()*ratio))
			self.updateTitle()
			if event.key() == QtCore.Qt.Key_Escape:
				self.close()
		if event.type() == QtCore.QEvent.MouseButtonPress:
			if event.pos().x() < self.size().width() -20:
			    self.diff = event.globalPos() - self.frameGeometry().topLeft()
			    self.mode = 'drag'
			else:
			    self.mode = 'resize'
		if event.type() == QtCore.QEvent.MouseMove:
			if self.mode == 'drag':
			    self.move(event.globalPos()-self.diff)
			else:
			    self.resize(event.pos().x(),event.pos().y())
			    self.updateTitle()
		return False
		

	def updateTitle(self):
		info = QtCore.QFileInfo(self.imageList[self.index])
		self.imagesizelabel.setText(str(self.imagesize.width()) +','+ str(self.imagesize.height()) + '    ->')
		self.title_label.setText(info.fileName())
		self.cursizelabel.setText('<-    ' + str(self.size().width()) + ',' + str(self.size().height()))

	def mousePressEvent(self,event):
		print(event.buttons())
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


# def main():
#     app = QtGui.QApplication(sys.argv)
#     imageview = ImageView()
#     sys.exit(app.exec_())


# if __name__ == '__main__':
#     main()
		