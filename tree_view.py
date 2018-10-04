# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets as QW
import subprocess, platform

#переопределил модель с целью установки собственных иконок каталогов
class CustomFileModel(QW.QFileSystemModel):

    all=0

    def __init__(self, parent = None):
        QW.QFileSystemModel.__init__(self, parent)
        self.icon = QtGui.QIcon('styles/images/folder.png')

    def data(self, index, role=None):
        if index.isValid() and role == QtCore.Qt.DecorationRole:
            if self.fileInfo(index).isRoot():
                return  self.icon# своя иконка для корневого каталога системы
            else:
                return self.icon#своя иконка

        elif index.isValid() and role == QtCore.Qt.DisplayRole:
            return self.fileInfo(index).baseName()#собственное имя каталога, необходимо

#класс, отображающий дерево каталогов системы

class Tree_View(QW.QTreeView):

    def __init__(self, parent = None):
        QW.QTreeView.__init__(self, parent)

        #устанавливаем модель
        self.model = CustomFileModel()
        self.setModel(self.model)
        path = r'/home/'
        self.model.setRootPath(path)
        self.model.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.Dirs|QtCore.QDir.NoSymLinks|
                             QtCore.QDir.NoDotAndDotDot)#фильтры, чтобы выводились только директории

        self.setAnimated(True)

        #для справки по доступным командам, которые IDE выдаёт
        #h = QW.QHeaderView(QtCore.Qt.Horizontal)
        #h.setModel(self.model)

        #настраиваем заголовки модели
        head = self.header()#получили ссылку на заголовок
        head.setVisible(False)#скрыли его

        head.setSectionResizeMode(0, QW.QHeaderView.Stretch)#первая колонка должна занимать всё свободное пространство
        head.setStretchLastSection(False)#а последняя колонка не должна так делать

        for i in range(1,4):#скрываем остальные колонки, размер, тип, время изменения
            head.setSectionHidden(i, True)
            head.resizeSection(i, 0)
        #вообще можно свою модель написать...

        #обрабатываем сигнал выделения элемента дерева
        self.clicked.connect(self.item_choose)

        #настраиваем перетаскивание каталога в список элементов
        self.setDragEnabled(True)
        #self.setAcceptDrops(True)
        self.setDragDropMode(QW.QAbstractItemView.DragOnly)
        self.setSelectionMode(QW.QAbstractItemView.ExtendedSelection)

        #чтобы вся выделенная строка брала цвет из файла стиля
        pal = QtGui.QPalette()
        pal.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, QtGui.QBrush(QtGui.QColor(255,255,255)))#закрасим белым
        pal.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, QtGui.QBrush(QtGui.QColor(255,255,255)))
        self.setPalette(pal)

    #метод обработки сигнала clicked - щелчка мыши над элементом дерева
    def item_choose(self, index):
        #print(index)
        q = self.model.filePath(index)
        print( self.currentIndex())
        print(q)

    #найдёт в дереве переданный путь из каталога каталогов
    def to_folder(self, path):
        print('in tree view',path)
        self.selectionModel().setCurrentIndex(self.model.index(path,0), QtCore.QItemSelectionModel.ClearAndSelect)

    def open_item(self, path):
        if platform.system() == 'windows':
            subprocess.Popen(["explorer", path])
        elif platform.system() == 'darwin':#OS X
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


#если запускаем как самостоятельный модуль
if __name__ == '__main__':
    import sys

    app = QW.QApplication(sys.argv)
    TreeViewWindow = Tree_View()
    TreeViewWindow.setMinimumSize(400,50)
    TreeViewWindow.show()

    sys.exit(app.exec_())
