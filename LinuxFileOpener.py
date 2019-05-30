import os, subprocess, sys
#from ProcessThread import *
import getpass

if sys.platform != 'win32': 
    document_location = os.path.join('/home',getpass.getuser(),'.Searcher')
    if not os.path.isdir(document_location):
        os.mkdir(document_location)
else:
    document_location = os.path.join('C:\\Users',getpass.getuser(),'Documents','Searcher')
    if not os.path.isdir(document_location):
        os.mkdir(document_location)

default_applications = os.path.join(document_location,'default applications.txt')
mimeapplist = os.path.join('/home',getpass.getuser(), '.local','share','applications','mimeapps.list')


class LinuxFileOpener():
    def __init__(self):
        self.app_dict = {}
        if os.path.isfile(default_applications):
            self.importAppDict()
        else:
            self.importMimeList()

    def importMimeList(self):
        mime = open(mimeapplist,'r')
        app_dict = open(default_applications,'w+')
        for line in mime:
            if line=='\n':break
            if line=='[Default Applications]\n':continue
            line = line.strip('\n')
            line = line.strip(';')
            line = line[:line.find('.')]
            _type,value = line.split('=')
            self.app_dict[_type]=value
            string = _type + ':' + value + '\n'
            app_dict.write(string)
        mime.close()
        app_dict.close

    def addToList(self,filetype,app):
        self.app_dict[filetype]=app
        self.updateDefaultList()  

    def importAppDict(self):
        if os.path.isfile(default_applications):
            f = open(default_applications,'r')
            for line in f:
                line = line.strip('\n')
                _type,app = line.split(':')
                self.app_dict[_type] = app


    def updateDefaultList(self):
        f= open(default_applications,'w+')
        for key,value in self.app_dict.items():
            string = key + ':' + value + '\n'
            f.write(string)
        f.close()


    def checkList(self,path):
        file_type = self.xdgQuery('filetype',path)
        if file_type in self.app_dict: return True
        return False


    def openFile(self,path):
        file_type = self.xdgQuery('filetype',path)
        #self.process = ProcessThread(self.app_dict[file_type],path)
        subprocess.Popen([self.app_dict[file_type],path])

    def xdgQuery(self, command, path):
        p = subprocess.Popen(['xdg-mime', 'query', command, path],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
        if p.returncode or errors:
            raise XDGError('xdg-mime returned error code %d: %s' %
                           (p.returncode, errors.strip()))
        if command == 'default':
            return output
        return output.strip().decode('utf-8')


    def setXdgDefault(self, app, app_type):
        subprocess.call(['xdg-mime', 'default', app, app_type])



class XDGError(Exception): pass

def main():
    linux = LinuxFileOpener()
    linux.importMimeList()
    linux.updateDefaultList()
    for key,value in linux.app_dict.items():
        print(key,value)
    linux.openFile(r'/home/yuuki')
        

if __name__ == '__main__':
    main()

    
