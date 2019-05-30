from PySide import QtGui, QtCore
from PySide.phonon import Phonon
import sys
 


class MusicPlayer(QtGui.QWidget):
	def __init__(self):
		super(MusicPlayer,self).__init__()

		self.sources = []
		self.music = []
		self.index = 0

		self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory,self)
		self.player = Phonon.MediaObject(self)
		self.metaInfo = Phonon.MediaObject(self)

		self.label = QtGui.QLabel(self)
		self.label.setText('Playing: ')
		Phonon.createPath(self.player,self.audioOutput)
		self.player.setTickInterval(1000)

		self.createActions()
		self.initUI()
		self.setWindowTitle('music player')
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.show()

	def createActions(self):
		self.playAction = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaPlay),'play',self)
		self.playAction.triggered.connect(self.player.play)

		self.pauseAction = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaPause),'pause',self)
		self.pauseAction.triggered.connect(self.player.pause)

		self.stopAction = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaStop),'stop',self)
		self.stopAction.triggered.connect(self.player.stop)

		self.nextAction = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaSkipForward),'next',self)
		self.nextAction.triggered.connect(self.next)

		self.prevAction = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_MediaSkipBackward),'prev',self)
		self.prevAction.triggered.connect(self.prev)

		self.addfileAction= QtGui.QAction('add files',self)
		self.addfileAction.triggered.connect(self.addFiles)

	def initUI(self):
		bar = QtGui.QToolBar(self)
		bar.addAction(self.playAction)
		bar.addAction(self.pauseAction)
		bar.addAction(self.stopAction)
		bar.addAction(self.prevAction)
		bar.addAction(self.nextAction)	

		self.seekSlider = Phonon.SeekSlider(self)
		self.seekSlider.setMediaObject(self.player)

		self.volumeSlider = Phonon.VolumeSlider(self)
		self.volumeSlider.setAudioOutput(self.audioOutput)
		self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Maximum)

		self.musicTable = QtGui.QTableWidget(0,1)
		headers = ['Title']
		self.musicTable.setHorizontalHeaderLabels(headers)
		self.musicTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.musicTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.musicTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.musicTable.cellClicked.connect(self.tablePlay)

		mainlayout = QtGui.QVBoxLayout(self)
		horilayout = QtGui.QHBoxLayout(self)
		mainlayout.addWidget(self.seekSlider)
		horilayout.addWidget(bar)
		horilayout.addStretch()
		horilayout.addWidget(self.volumeSlider)
		mainlayout.addLayout(horilayout)
		mainlayout.addWidget(self.label)
		mainlayout.addWidget(self.musicTable)


		menu = QtGui.QMenuBar(self)
		filemenu= menu.addMenu('&File')
		filemenu.addAction(self.addfileAction)

		mainlayout.setMenuBar(menu)

		self.resize(500,300)

	def addFiles(self):
		files, _ = QtGui.QFileDialog.getOpenFileNames(self,self.tr("Select Music Files"),QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation))
		for string in files:
			self.sources.append(Phonon.MediaSource(string))
		if self.sources:
			self.updateTable()

		self.player.setCurrentSource(self.sources[0])
		self.label.setText('Playing: ' + self.player.currentSource().fileName().split('/')[-1])
		self.player.play()

	def tablePlay(self):
		self.index = self.musicTable.currentRow()
		self.player.setCurrentSource(self.sources[self.index])
		self.label.setText('Playing: ' + self.player.currentSource().fileName().split('/')[-1])
		self.player.play()

	def next(self):
		if self.index+1 < len(self.sources):
			self.index+=1
			self.player.setCurrentSource(self.sources[self.index])
		else:
			self.index = 0
			self.player.setCurrentSource(self.sources[self.index])
		self.label.setText('Playing: ' + self.player.currentSource().fileName().split('/')[-1])
		self.player.play()

	def prev(self):
		if self.index-1 >= 0:
			self.index-=1
			self.player.setCurrentSource(self.sources[self.index])
		else:
			self.index = len(self.sources)-1
			self.player.setCurrentSource(self.sources[self.index])
		self.label.setText('Playing: ' + self.player.currentSource().fileName().split('/')[-1])	
		self.player.play()


	def updateTable(self):
		while self.musicTable.rowCount()>0:
			self.musicTable.removeRow(0)
		for item in self.sources:
			self.metaInfo.setCurrentSource(item)
			title = self.metaInfo.currentSource().fileName().split('/')[-1]
			titleItem = QtGui.QTableWidgetItem(title)
			current_row = self.musicTable.rowCount()
			self.musicTable.insertRow(current_row)
			self.musicTable.setItem(current_row,0,titleItem)


	def startMusic(self,music_path):
		self.player.setCurrentSource(Phonon.MediaSource(music_path))
		if music_path not in self.music:
			self.music.append(music_path)
			self.sources.append(Phonon.MediaSource(music_path))
		self.updateTable()
		self.label.setText('Playing: ' + self.player.currentSource().fileName().split('/')[-1])
		self.player.play()

def main():
    app = QtGui.QApplication(sys.argv)
    music = MusicPlayer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
