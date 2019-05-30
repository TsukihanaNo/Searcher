import os, sys, subprocess
from PySide import QtCore,QtGui


class ProcessThread(QtCore.QThread):
    def __init__(self,program,path):
        super(ProcessThread,self).__init__()
        self.path = path
        self.program = program

    def run(self):
        subprocess.call([self.program,self.path])
