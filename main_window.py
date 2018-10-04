# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets as QW

from PyQt5.QtCore import QSettings

#from PyQt5.QtGui import QStyleFactory

import tag_table
import tree_view
import item_list

import sys

app = QW.QApplication(sys.argv)

class TagMaker_Window(QW.QMainWindow):
    #конструктор
    def __init__(self, parent=None):
        QW.QWidget.__init__(self, parent)
        self.setWindowTitle('TagMaker')
        self.setMinimumSize(600, 300)  # размеры окна

        self.workplace = QW.QWidget(self)#добавляем место для вкладок и файлов
        self.setCentralWidget(self.workplace)#основное пространство

        self.main_grid = QW.QGridLayout()#сетка для выравнивания, в ней будет три-четыре элемента в одну строку, плюс пустые столбцы
        #self.main_grid.setAlignment(QtCore.Qt.AlignTop)#со сплиттером лучше отключить выравнивание
        self.workplace.setLayout(self.main_grid)

        #создание панели вкладок, класс в другом модуле
        tab_widget = QW.QWidget()
        self.tag_tab = tag_table.TagTabs(self)
        self.tag_tab.setMinimumWidth(250)#250 - пока оптимальный размер



        tab_layout = QW.QVBoxLayout()
        tab_buttons_layout = QW.QHBoxLayout()
        #создание управляющих кнопок
        self.addTab_button = QW.QPushButton()
        self.delete_tag_button = QW.QPushButton()
        self.appTag_button  = QW.QPushButton()
        self.findMode_button  = QW.QPushButton() #кнопка для переключения режимов поиска и назначения
        self.find_button  = QW.QPushButton()

        self.addTab_button.setFixedSize(QtCore.QSize(30,30))
        self.delete_tag_button.setFixedSize(QtCore.QSize(30,30))
        self.appTag_button.setFixedSize(QtCore.QSize(30,30))
        self.findMode_button.setFixedSize(QtCore.QSize(30, 30))
        self.find_button.setFixedSize(QtCore.QSize(30, 30))


        self.addTab_button.clicked.connect(self.tag_tab.add_tab_dialog)
        self.delete_tag_button.clicked.connect(self.tag_tab.change_checkbox)
        self.appTag_button.clicked.connect(self.app_tags)

        self.findMode_button.clicked.connect(self.find_tag_mode)
        self.findMode_button.setCheckable(True)
        self.find_button.setDisabled(True)
        self.find_button.clicked.connect(self.find_by_tags)

        #иконки к кнопкам
        self.addTab_button.setIcon(QtGui.QIcon('styles/images/add_tab_btn.png'))
        self.addTab_button.setIconSize(QtCore.QSize(25,25))
        self.addTab_button.setToolTip('Add a new tab')

        self.delete_tag_button.setIcon(QtGui.QIcon('styles/images/del_tag_btn.png'))
        self.delete_tag_button.setIconSize(QtCore.QSize(20,20))
        self.delete_tag_button.setToolTip('Delete selected tags')

        self.appTag_button.setIcon(QtGui.QIcon('styles/images/tag_to_folder.png'))
        self.appTag_button.setIconSize(QtCore.QSize(20, 20))
        self.appTag_button.setToolTip('App checked tags to folder')

        self.find_button.setIcon(QtGui.QIcon('styles/images/search.png'))
        self.find_button.setIconSize(QtCore.QSize(20, 20))
        self.find_button.setToolTip('Find by checked tags')

        self.findMode_button.setIcon(QtGui.QIcon('styles/images/search_mode.png'))
        self.findMode_button.setIconSize(QtCore.QSize(20, 20))
        self.findMode_button.setToolTip('Find mode on/off')

        tab_buttons_layout.addWidget(self.addTab_button)
        tab_buttons_layout.addWidget(self.delete_tag_button)
        tab_buttons_layout.addWidget(self.appTag_button)
        tab_buttons_layout.addWidget(self.findMode_button)
        tab_buttons_layout.addWidget(self.find_button)

        #tab_buttons_layout.addWidget(ch)

        tab_buttons_layout.addStretch(0)

        tab_layout.addLayout(tab_buttons_layout)
        tab_layout.addWidget(self.tag_tab)

        tab_widget.setLayout(tab_layout)

        #self.tag_tab.resize(50,0)

        #список добавленных объектов
        item_widget = QW.QWidget()
        self.item_list = item_list.Item_List(self)
        self.item_list.setMinimumWidth(150)
        #кнопки к нему
        item_layout = QW.QVBoxLayout()
        item_buttons_layout = QW.QHBoxLayout()

        delete_item_button = QW.QPushButton()
        delete_item_button.setFixedSize(QtCore.QSize(30,30))
        delete_item_button.clicked.connect(self.item_list.delete_item)

        open_button = QW.QPushButton()
        open_button.setFixedSize(QtCore.QSize(30, 30))
        open_button.clicked.connect(self.open_item)

        in_tree_button = QW.QPushButton()
        in_tree_button.setFixedSize(QtCore.QSize(30, 30))
        in_tree_button.clicked.connect(self.find_in_tree)

        #строка поиска объектов
        find_line = self.item_list.find_line

        #иконки
        delete_item_button.setIcon(QtGui.QIcon('styles/images/del_folder_btn.png'))
        delete_item_button.setIconSize(QtCore.QSize(20, 20))
        delete_item_button.setToolTip('Delete folder from list')

        open_button.setIcon(QtGui.QIcon('styles/images/open_folder.png'))
        open_button.setIconSize(QtCore.QSize(20, 20))
        open_button.setToolTip('Open folder in explorer')

        in_tree_button.setIcon(QtGui.QIcon('styles/images/in_tree.png'))
        in_tree_button.setIconSize(QtCore.QSize(20, 20))
        in_tree_button.setToolTip('View in tree')

        item_buttons_layout.addWidget(delete_item_button)
        item_buttons_layout.addWidget(open_button)
        item_buttons_layout.addWidget(in_tree_button)

        item_buttons_layout.addWidget(find_line)
        item_layout.addLayout(item_buttons_layout)
        item_layout.addWidget(self.item_list)

        #item_buttons_layout.addStretch(0)

        item_widget.setLayout(item_layout)

        #дерево каталогов
        self.folder_list = tree_view.Tree_View(self)

        #разделитель для изменения ширины
        self.tag_splitter = QW.QSplitter(QtCore.Qt.Horizontal, self)
        self.tag_splitter.setChildrenCollapsible(False)
        self.tag_splitter.addWidget(tab_widget)#добавили флажки

        self.tag_splitter.addWidget(item_widget)#список с элементами

        self.tag_splitter.addWidget(self.folder_list)#дерево каталогов

        self.main_grid.addWidget(self.tag_splitter, 0, 0)


        #self.add_toolbar()#добавить тулбар, это метод #перешли к другому расположению кнопок

        #этот сигнал приходит из списка каталогов, когда в этом списке выбран каталог. нужен для синхронизации тегов и вкладок
        self.item_list.selectionModel().selectionChanged.connect(self.choose_checkbox)


        #разобраться с сохранением данных
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('JUJ')
        settings.setValue('x', [100,200])
        settings.endGroup()


    #передача тегов в item_list из tab_table
    def app_tags(self):
        name, tags = self.tag_tab.app_checkbox_to_folder()
        print('main', tags)
        self.item_list.write_tags(name, tags)
        #теперь можем передать список тего в   item_list, и там обработать

    def choose_checkbox(self):
        print('in choose_checkbox',self.item_list.temp_tab_tags)

        self.tag_tab.mark_checkbox(self.item_list.temp_tab_tags)

    def find_tag_mode(self):
        if self.findMode_button.isChecked():
            self.addTab_button.setDisabled(True)
            self.appTag_button.setDisabled(True)
            self.delete_tag_button.setDisabled(True)
            self.find_button.setEnabled(True)

            self.tag_tab.mark = False# чтобы не отмечались флажки в режиме поиска по тегам

        else:
            self.addTab_button.setDisabled(False)
            self.appTag_button.setDisabled(False)
            self.delete_tag_button.setDisabled(False)
            self.find_button.setEnabled(False)

            self.item_list.find_item_tags({}, findTrue = False)#чтобы активировать все каталоги
            self.tag_tab.mark = True# чтобы снова отмечались флажки в режиме назначения тегов


    #непосредственно запуск поиска по тегам
    def find_by_tags(self):
        checked_tags = self.tag_tab.find_item_by_tag()
        if checked_tags:
            self.item_list.find_item_tags(checked_tags, findTrue = True)
        else:
            print('empty checked tags')
            self.item_list.find_item_tags(checked_tags, findTrue = False)#чтобы активировать все каталоги


    def find_in_tree(self):
        for i in self.item_list.selectionModel().selectedIndexes():
            cur_item = self.item_list.model.data(i, role=QtCore.Qt.UserRole)
            self.folder_list.to_folder(cur_item)

    def open_item(self):
        for i in self.item_list.selectionModel().selectedIndexes():
            cur_item = self.item_list.model.data(i, role=QtCore.Qt.UserRole)
            self.folder_list.open_item(cur_item)


    #событие закрытия окна
    def closeEvent(self, QCloseEvent):
        #тут надо будет сохранить параметры окна в QSettings, и восстанавливать их потом в конструкторе
        pass#self.tab_db.close()



if __name__ == '__main__':

    tagMakerWindow = TagMaker_Window()
    tagMakerWindow.setMinimumSize(700,400)

    tagMakerWindow.setWindowIcon(QtGui.QIcon('icons/icon.png'))
    app.setWindowIcon(QtGui.QIcon('icons/icon.png'))

    f = open('styles/exp_style.stylesheet', 'r')
    styleData = f.read()
    f.close()
    app.setStyleSheet(styleData)

    tagMakerWindow.show()
    sys.exit(app.exec_())
