"""
============================================
Archives Management Library
============================================
It uses shutil to manage zip and tar.gz files

"""

import os
# import sys
import tarfile
import zipfile
import shutil


def targz(file, path='.'):
    """tar and gz a dir into file
    ".tar.gz" will be added to the filename
    """
    if (len(file) >7) and file[-7:] == ".tar.gz":
            file = file[:-7]
    try:
        shutil.make_archive(file, "gztar", base_dir=path)
    except Exception as err:
        raise Exception( "Unable to compress %s: %s" % (file, err))


def tar(file, path='.'):
    """tar a dir into file
    ".tar" will be added to the filename
    """
    if (len(file) >4) and file[-4:] == ".tar":
            file = file[:-4]
    try:
        shutil.make_archive(file, "tar", base_dir=path)
    except Exception as err:
        raise Exception( "Unable to extract %s: %s" % (file, err))


def untar(file, path='.'):
    """untar a file to a given path"""
    try:
        tar = tarfile.open(file)
        tar.extractall(path)
    except Exception as err:
        raise Exception( "Unable to extract %s: %s" % (file, err))


def zip(file, path='.'):
    """zip a dir into file
    ".zip" will be added to the filename
    """
    zip = Zipper(file)
    zip.zip(path)


def unzip(file, path='.'):
    """unzip a file to a given path"""
    zip = Zipper(file)
    zip.unzip(path)


class Zipper:
    """
    Zip/unzip a given file or folder
    """
    def __init__(self, file):
        self.file = file

    def zip(self, path='.'):
        """zip a dir into file
        ".zip" will be added to the filename
        """
        if (len(self.file) >4) and self.file[-4:] == ".zip":
                self.file = self.file[:-4]
        try:
            shutil.make_archive(self.file, "zip", root_dir=path, )#base_dir=path)
            #shutil.make_archive(self.file, "zip", base_dir=path) 
            #no root_dir, only base_dir preserves directory structrue
            #'root_dir' is a dir that will be the root directory of the archive
            #ie. we typically chdir into 'root_dir' before creating the archive. 
            #'base_dir' is the directory where we start archiving from;
            #ie. 'base_dir' will be the common prefix of all files 

        except Exception as err:
            raise Exception( "Unable to extract %s: %s" % (self.file, err))

    def unzip(self, path='.'):
        """unzip a file to a given path"""
        zipo = self.__get_zip_file_obj()
        try:
            zip = zipo.extractall(path)
            zipo.close()
        except Exception as err:
            raise Exception( "Unable to extract %s: %s" % (self.file, err))

    def test(self, file):
        """checks whether zip file is good or bad
           returns True if good.
           returns False if corrupted.
        """
        try:
            if not os.path.isfile(self.file):
                raise Exception('File not found')
            if not zipfile.is_zipfile(self.file):
                raise Exception ('Not a zip file')
            zipo = self.__get_zip_file_obj()
            iszip = zipo.testzip()
            if iszip is not None:
                raise Exception(iszip)
            zipo.close()
        except Exception as err:
            raise zipfile.BadZipfile( "Corrupt Archive %s: %s" % (self.file, err))
        return True

    def get_filelist(self):
        """
        Returns the list of files contained in a zip file
        """
        list = []
        zipo = self.__get_zip_file_obj()
        for i in zipo.infolist():
            list.append(i.filename)
        zipo.close()
        return list

    def __get_zip_file_obj(self):        
        """internal function. returns ZipFile object"""
        try :
            zipo = zipfile.ZipFile(file = self.file, 
                            mode = 'r',
                            compression = zipfile.ZIP_DEFLATED,
                            allowZip64 = False)
        except:
            try:
                zipo = zipfile.ZipFile(file = self.file,
                                mode = 'r',
                                compression = zipfile.ZIP_DEFLATED)
            except Exception as err:
                raise zipfile.BadZipfile( "Unable to open zip file %s : %s" % (self.file, err))
        return zipo
