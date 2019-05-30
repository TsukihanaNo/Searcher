import os, sys, time, getpass
from PySide import QtCore, QtGui


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

file_count = os.path.join(archivefolder, 'counts.txt')
export_file = os.path.join(archivefolder, 'foundfiles.txt')
search_locations = os.path.join(archivefolder, 'locations.txt')
path_archive = os.path.join(archivefolder, 'path archive.txt')
restricted_file = os.path.join(archivefolder, 'restricted folders.txt')
error_log_file = os.path.join(archivefolder, 'error log.txt')
exception_file = os.path.join(archivefolder, 'exception.txt')



class UpdateThread(QtCore.QThread):
    def __init__(self):
        super(UpdateThread, self).__init__()
        self.pathlist = []
        self.dir_count = 0
        self.file_count = 0
        self.restricted_dir = []
        self.root_search_list = []
        self.search_exception_list = []
        self.restricted_dir_count = 0

    def run(self):
        start = time.time()
        self.GetSetting()
        self.MainCrawler()
        self.CreateArchive()
        self.CreateRestrictedFolder()
        #self.GetMonitorInfo()
        #self.CreateMonitorArchive()
        end = time.time()
        print(end - start)
        return (self.pathlist, self.file_count, self.dir_count)

    def MainCrawler(self):
        for item in self.root_search_list:
            self.SubCrawler(item)
        date_time = QtCore.QDateTime().currentDateTime().toString('MM.dd.yyyy - hh:mm:ss AP')
        self.pathlist.append(date_time)

    def CreateArchive(self):
        date_time = QtCore.QDateTime().currentDateTime().toString('MM.dd.yyyy - hh:mm:ss AP')
        f = open(path_archive, 'w+')
        x=0
        for a in self.pathlist:
            try:
                if x ==0:
                    f.write(date_time)
                    f.write('\n')
                    x+=1
                f.write(a)
                f.write("\n")
            except UnicodeEncodeError:
                error = 'couldnt add: ' + a + ' to file'
        f.close()
        f = open(file_count, 'w+')
        for item in [self.dir_count, self.file_count]:
            f.write(str(item))
            f.write('\n')
        f.close()

    def CreateRestrictedFolder(self):
        f = open(restricted_file, 'w+')
        for item in self.restricted_dir:
            try:
                f.write(item)
                f.write('\n')
            except UnicodeEncodeError:
                print(UnicodeEncodeError)
        f.close()

    def SubCrawler(self, dir):
        QtGui.QApplication.processEvents()
        try:
            for filename in os.listdir(dir):
                path = os.path.join(dir, filename)
                if path not in self.search_exception_list:
                    # if the path is not a directory, then add it to the list
                    if not os.path.isdir(path):
                        self.pathlist.append(path)
                        self.file_count += 1
                    else:
                        # if it is a directory, we must dive deeper
                        self.pathlist.append(path)
                        self.dir_count += 1
                        self.SubCrawler(path)
        except:
            print('encountered an error with dir: ' + dir)
            self.restricted_dir.append(dir)
            self.restricted_dir_count += 1

    def GetSetting(self):
        self.root_search_list = []
        self.search_exception_list = []
        f = open(search_locations, 'r')
        for line in f:
            self.root_search_list.append(line.rstrip('\n'))
        f.close()
        f = open(exception_file, 'r')
        for line in f:
            self.search_exception_list.append(line.rstrip('\n'))
        f.close()


    def GetMonitorInfo(self):
        self.totalsize = 0
        for item in self.pathlist:
            QtGui.QApplication.processEvents()
            if os.path.isfile(item):
                self.totalsize += os.path.getsize(item)

    def CreateMonitorArchive(self):
        date = QtCore.QDate()
        date1 = date.currentDate().toString('MM.dd.yyyy').split('.')  # month, date, year
        filename = date1[0] + '.' + date1[2] + '.csv'
        path = os.path.join(monitor_archive, filename)
        lines = []
        if os.path.isfile(path):
            f = open(path, 'r')
            for line in f:
                print(line)
                lines.append(line.rstrip('\n'))
            f.close()
        f = open(path, 'w+')
        current_date = date.currentDate().toString('MM.dd.yyyy')
        new_info = current_date + ' , ' + str(self.totalsize / (1024 * 1024)) + ' , ' + str(
            self.file_count) + ' , ' + str(self.dir_count)
        if current_date in lines[-1]:
            lines[-1] = new_info
        else:
            lines.append(new_info)
        for item in lines:
            try:
                print(item)
                f.write(item)
                f.write('\n')
            except:
                print('error writing to file')





