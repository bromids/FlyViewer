#!/usr/bin/python3
# coding:utf-8

import sys,os
from PyQt5 import QtWidgets,QtGui
VERSION='0.1'

def main():
    app=QtWidgets.QApplication(sys.argv)
    screen=Form()
    screen.show()

    sys.exit(app.exec_())

class PicPanel(QtWidgets.QWidget):
    def __init__(self,pix=None,pixdir='',parent=None):
        super().__init__(parent)
        self.cursel=[0,0,0]
        self.pix=self._populatepix(pixdir) if pix==None else pix
        self._initLayout()

    def _populatepix(self):
        pix={}
        for f0 in os.listdir(pixdir):
            f0d=os.path.join(pixdir,f0)
            pix[f0]={}
            for f1 in os.listdir(f0d):
                f1d=os.path.join(f0d,f1)
                pix[f0][f1]={}
                for f2 in os.listdir(f1d):
                    f2d=os.path.join(f1d,f2)
                    pix[f0][f1][f2]=[os.path.join(f2d,s) for s in os.listdir(f2d)]
                    if len(pix[f0][f1][f2])>1:
                        print('Warning: Ignored second file in same folder:\n\t','\n\t'.join(pix[f0][f1][f2]))
        return pix

    def updateList0(self):
        self.lists[0].clear()
        self.lists[0].addItems(sorted([s for s in self.pix]))
        self.lists[0].setCurrentRow(0)

    def updateList1(self):
        self.lists[1].clear()
        self.lists[1].addItems(sorted([s for s in self.pix[self.lists[0].currentItem().text()]]))
        self.lists[1].setCurrentRow(0)

    def updateList2(self):
        self.lists[2].clear()
        [t1,t2]=[self.lists[0].currentItem().text(),
                 self.lists[1].currentItem().text()]
        self.lists[2].addItems(sorted([s for s in self.pix[t1][t2]]))
        self.lists[2].setCurrentRow(0)

    def updateImage(self):
        [t1,t2,t3]=[self.lists[0].currentItem().text(),
                    self.lists[1].currentItem().text(),
                    self.lists[2].currentItem().text()]
        self.txt.setText(self.pix[t1][t2][t3][0])
        limg=QtGui.QPixmap(self.pix[t1][t2][t3][0])
        limg.scaledToWidth(True)
        self.img.setPixmap(limg)
        
    def _initLayout(self):
        def updateList1(row):
            if row!=-1:
                self.updateList1()
            
        def updateList2(row):
            if row!=-1:
                self.updateList2()

        def updateImage(row):
            if row!=-1:
                self.updateImage()

        self.txt=QtWidgets.QLineEdit()
        self.lists=[]
        for y in range(3):   # a/b/c
            self.lists.append(QtWidgets.QListWidget())
        self.img=QtWidgets.QLabel()
        self.img.setScaledContents(True)

        self.updateList0()
        self.updateList1()
        self.updateList2()
        self.updateImage()
        
        VB0=QtWidgets.QVBoxLayout()
        HB1=QtWidgets.QHBoxLayout()
        for i in range(3):
            HB1.addWidget(self.lists[i])
        VB0.addWidget(self.img)
        VB0.addWidget(self.txt)
        VB0.addLayout(HB1)
        
        self.lists[0].currentRowChanged.connect(updateList1)
        self.lists[1].currentRowChanged.connect(updateList2)
        self.lists[2].currentRowChanged.connect(updateImage)
        self.setLayout(VB0)

                
class Form(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(Form,self).__init__(parent)
        if not os.path.isfile('Settings.conf'):
            QtWidgets.QMessageBox.warning(self,'No Settings.conf file found','The settings file could not be found.  Please specify the image directory.')
            self.pixdir=self.getPath()
        else:
            self.pixdir=self.getpixdir()
        self.pix=self.populatepix()
        self._initMenu()
        self._initLayout()

    def _initLayout(self):
        self.panels=[PicPanel(self.pix,self.pixdir,self),PicPanel(self.pix,self.pixdir,self)]

        self.VB=QtWidgets.QVBoxLayout()
        self.VB.addWidget(self._initMenu())

        HB0=QtWidgets.QHBoxLayout()
        HB0.addWidget(self.panels[0])
        HB0.addWidget(self.panels[1])

        self.VB.addLayout(HB0)
            
        self.setLayout(self.VB)
        self.setWindowTitle('Fly Viewer v. {}'.format(VERSION))

    def _initMenu(self):
        mbar=QtWidgets.QMenuBar() 
        mFile=mbar.addMenu('&File')
        mEdit=mbar.addMenu('&Edit')
        mPath=QtWidgets.QAction('&Change Directory',mbar)
        mQuit=QtWidgets.QAction('&Quit',mbar)
        mBW=QtWidgets.QAction('&Black and White',mbar,checkable=True)

        mPath.triggered.connect(self.getPath)
        mQuit.triggered.connect(self.close)

        mFile.addAction(mPath)
        mFile.addAction(mQuit)
        mEdit.addAction(mBW)

        return mbar

    def getPath(self):
        confpath=QtWidgets.QFileDialog.getExistingDirectory(self,'Image Directory','/mnt/',QtWidgets.QFileDialog.ShowDirsOnly)
        while not os.path.isdir(confpath):
            QtWidgets.QMessageBox.warning(self,'No such directory','The image directory was not found.  Please choose a valid existing directory.')
            confpath=QtWidgets.QFileDialog.getExistingDirectory(self,'Image Directory','/mnt/',QtWidgets.QFileDialog.ShowDirsOnly)
        with open('Settings.conf','w') as settings:
            settings.write('pixdir=%s'%confpath)
        return confpath
        
    def getpixdir(self):
        with open('Settings.conf','r') as f:
            for line in f:
                if line[:7]=='pixdir=':
                    pixdir=line.split('=')[1].replace('\n','')+'/'
        if not os.path.isdir(pixdir):
            chdir=QtWidgets.QMessageBox.question(self,'No such directory','Settings.conf points to a nonexistant directory.  Change directory?',
                                           QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No,
                                           QtWidgets.QMessageBox.No)
            if chdir==QtWidgets.QMessageBox.Yes:
                return self.getPath()
            else:
                return self.getpixdir()
        else:
            return pixdir

    def populatepix(self):        
        pix={}
        for f0 in os.listdir(self.pixdir):
            f0d=os.path.join(self.pixdir,f0)
            pix[f0]={}
            for f1 in os.listdir(f0d):
                f1d=os.path.join(f0d,f1)
                pix[f0][f1]={}
                for f2 in os.listdir(f1d):
                    f2d=os.path.join(f1d,f2)
                    pix[f0][f1][f2]=[os.path.join(f2d,s) for s in os.listdir(f2d)]
                    if len(pix[f0][f1][f2])>1:
                        print('Warning: Ignored second file in same folder:\n\t','\n\t'.join(pix[f0][f1][f2]))
        return pix
        

if __name__=='__main__':
    main()
