# -*- coding: utf-8 -*-

from PyQt5 import QtCore, Qt, QtGui, QtSql, QtWidgets as QW
import os.path, sys

if __name__ == '__main__':
    app = QW.QApplication(sys.argv)


#класс, отображающий добавленные в базу папки


class Item_List(QW.QListView):


    def __init__(self, parent = None):
        QW.QListView.__init__(self, parent)

        self.model = QtGui.QStandardItemModel()
        self.setModel(self.model)

        #self.setAlternatingRowColors(True) #позволяет раскрашивать чередующиеся строки через стиль или как-то иначе
        #self.setSelectionMode(QW.QAbstractItemView.SingleSelection)#режим выделения с Ctrl
        self.setMovement(QW.QListView.Free)

        #self.setGridSize(QtCore.QSize(145, 30))

        #если щёлкаем на элементе списка
        #self.clicked.connect(self.item_choose)
        #НУЖНО СДЕЛАТЬ ПО ВЫДЕЛЕНИЮ, В ТОМ ЧИСЛЕ С КЛАВИАТУРЫ
        #вот, сделал:
        self.selectionModel().selectionChanged.connect(self.item_choose)#по модели выделения
        #установил одиночное выделение
        self.setSelectionMode(QW.QAbstractItemView.ExtendedSelection)
        '''
        self.setResizeMode(QW.QListView.Adjust)  # подгоняем размещение элементов под размер списка
        self.setFlow(QW.QListView.LeftToRight)#направление вывода
        self.setWrapping(True)#перенос элементов на новую строку разрешён
        self.setWordWrap(True)#перенос элементов на новую строку разрешён

        width_size = QtCore.QSize(400, 30)
        self.setGridSize(width_size)  # задаём размеры таблицы размещения, 200 - макс. длина строки до
        # обрезки текста, 30 - отступ между строками по вертикали
        '''
        #строка поиска
        self.find_line = QW.QLineEdit()
        self.find_line.textChanged.connect(self.find_item)
        self.find_line.setPlaceholderText('Search...')
        validator = QtGui.QRegExpValidator(QtCore.QRegExp('\w{0,}.{0,}'))
        self.find_line.setValidator(validator)  # добавили валидатор по созданному регулярному выражению

        #настройка перетаскивания
        self.setDragEnabled(True)
        self.setAcceptDrops(True)#разрешаем сброс
        self.setDropIndicatorShown(True)

        self.setDragDropMode(QW.QAbstractItemView.InternalMove)#такая настройка позволит окончательно разрешить drag&drop...

        self.exist_path = []  # список, в который будем заносить существующие пути в базе
        self.cur_item = ''  # путь к выделенному объекту
        self.table_count = 0  # нужен для именования таблиц
        self.temp_tab_tags = {}  # нужен для передачи в tab_table и отметки тегов
        self.mult = []

        self.connect_sql()#соединение с бд


        #метод, который вызывается системой, когда что-то перетаскивается в этот список
    def dragEnterEvent(self, event):
        event.setDropAction(QtCore.Qt.ActionMask)
        #print(event.dropAction())
        if event.mimeData().hasUrls():
            #print(event.mimeData().urls())
            event.accept()
        else:
            event.ignore()

    #когда перетаскиваемый объект сброшен
    def dropEvent(self, QDropEvent):
        QDropEvent.setDropAction(QtCore.Qt.ActionMask)

        self.item_data.transaction()#запускаем транзакцию для ускорения команды INSERT, которая вызывается в методе create_item

        for p in range(len(QDropEvent.mimeData().urls())):#если выделено несколько элементов, мы добавляем их из этого списка
            #надо было сразу смотреть класс qUrl !!!
            path = QDropEvent.mimeData().urls()[p]
            self.create_item(path.path())#основной метод создания объекта в модели

        self.item_data.commit()

        '''
        #проверка
        query = QtSql.QSqlQuery(self.item_data)
        query.exec('select count(path) as nums from items')
        query.first()
        print("всего записей каталогов:", query.value('nums'))
        query.finish()
        '''



    #прямой метод добавления папки
    def create_item(self, path, write_to_data = True):
        #print('create item', path)
        if path not in self.exist_path and os.path.exists(path) and os.path.isdir(path):#проверяем так же, что каталог ещё на диске
            if path == '/':  # в Linux это корневой каталог, basename что-то не возвращает его самого
                item = QtGui.QStandardItem('/')
            else:
                item = QtGui.QStandardItem(os.path.basename(path))  # чтобы только имя каталога отображалось


            item.setEditable(False)  # нельзя редактировать имя в базе

            icon = QtGui.QIcon('styles/images/folder.png')
            #icon.addFile()
            item.setIcon(icon)  # установили иконку из доступных в теме ОС

            self.model.appendRow(item)  # добавили элемент список

            # назначаем в пользовательскую роль элемента путь до него. в список же будет выводиться только название каталога, не путь до него
            i = self.model.indexFromItem(item)  # индекс только что добавленного элемента
            self.model.setData(i, path, role=QtCore.Qt.UserRole)  # индекс роли - 32, в эту роль сохраняем путь

            # print(item.data(role = QtCore.Qt.UserRole))#выведем данные роли
            print('DATA',self.model.data(i, role=QtCore.Qt.UserRole))#аналогично предыдущей команде

            self.exist_path.append(path)

            if write_to_data:
                self.write_item_data(path)


    #метод выполняется, когда выбирается элемент списка
    def item_choose(self, selection):

        #print(selection.indexes())
        print(self.selectionModel().selectedIndexes())

        #self.cur_item = self.model.data(first, role=QtCore.Qt.UserRole)

        #self.mult.append(self.cur_item)
        self.temp_tab_tags = {}
        tab, tag = '', ''
        for cur in self.selectionModel().selectedIndexes():
            print('CHOOSE',self.model.data(cur, role=QtCore.Qt.UserRole))
            path = self.model.data(cur, role=QtCore.Qt.UserRole)
            #это для того, чтобы передать вкладки и теги в main, а затем в tab_table
            for table in self.item_data.tables():  # просмотрели все таблицы
                #print(table)
                query = QtSql.QSqlQuery(self.item_data)

                # нашли, что в этой таблице записан путь
                # к выбранному каталогу
                query.prepare('select tab, tags from {0} where exists (select path from {0} where path = (:path))'.format(table))

                query.bindValue(':path', path)
                print('path in choose', path)
                query.exec_()
                if query.isActive():
                    query.first()
                    while query.isValid():
                        print('tab:', query.value('tab'), 'tags:', query.value('tags'))
                        tab = query.value('tab')
                        tag = query.value('tags')
                        self.temp_tab_tags[tab] = tag.splitlines()  # разделит по пробельному символу, в том числе
                        # по символу перевода строки
                        query.next()
                query.finish()


        print(self.temp_tab_tags)
        #'''


    #метод удаления папки из списка и из бд, вызывается из main_window
    def delete_item(self):
        #if self.selectionModel().hasSelection():#проверка на то, что существует выбранный элемент
        #self.model.takeItem(self.currentIndex().row())
        #print('in delete',self.selectionModel().selectedIndexes())
        seli = set(self.selectionModel().selectedIndexes())
        print(seli)

        for cur in seli:
           # print(cur)
            deleted = self.model.data(cur, role=QtCore.Qt.UserRole)#self.cur_item
            #print('exists paths',self.exist_path, 'delete', deleted)
            #print(self.exist_path.index(deleted))
            if deleted in self.exist_path:
                self.exist_path.remove(deleted)
                #self.model.removeRow(cur.row())

            del_table = ''
            for table in self.item_data.tables():
                print(table)

                query = QtSql.QSqlQuery(self.item_data)
                query.prepare('select path from {0} where path = (:path)'.format(table))
                query.bindValue(':path', deleted)
                query.exec_()

                if query.isActive():
                    query.first()
                    while query.isValid():
                        if query.value('path'):
                            print('for delete: ', query.value('path'))
                            del_table = table
                        query.next()
                query.finish()

                if del_table:
                    query_drop = QtSql.QSqlQuery(self.item_data)
                    query_drop.exec('drop table if exists {0}'.format(del_table))
                    print('drop table {0}'.format(del_table))
                    #print(query_drop.lastError().text())  # database table is locked Unable to fetch row
                    query_drop.finish()

        self.delete_rows()

    #рекурсивный метод для удаления нескольких объектов
    def delete_rows(self):
            for index in self.selectionModel().selectedIndexes():
                # print(index)
                if self.selectionModel().isSelected(index):
                    self.model.removeRow(index.row())
                    self.delete_rows()

    #соединение или создание бд sqlite3
    def connect_sql(self):
        self.item_data = QtSql.QSqlDatabase.addDatabase('QSQLITE', connectionName = 'items')
        self.item_data.setDatabaseName('data//item_data')
        self.item_data.open()
        print(self.item_data.tables())

        '''
        if 'items' not in self.item_data.tables():
            query = QtSql.QSqlQuery(self.item_data)
            query.exec('create table items (path text COLLATE NOCASE, tab text COLLATE NOCASE, tags text COLLATE NOCASE)')
            print('создана основная таблица')
            query.finish()
        '''

        self.read_item_data()

    def write_item_data(self, path):

        print('добавляем элемент: ', path)

        #задали имя для таблицы
        name = '_'+str(self.table_count)+'_'

        while True:
            if name in self.item_data.tables():
                self.table_count +=1
                name = '_' + str(self.table_count) + '_'
            else:
                break

        #создали таблицу
        query = QtSql.QSqlQuery(self.item_data)
        query.exec('create table {0} (path text COLLATE NOCASE, '
                   'tab text UNIQUE COLLATE NOCASE, '
                   'tags text COLLATE NOCASE)'.format(name))
        print('создана таблица', name)
        query.finish()

        #вставили в таблицу путь к каталогу
        s = 'insert into {0}(path) values(:path)'.format(name)
        print(s)
        query.prepare(s)
        query.setForwardOnly(True)
        query.bindValue(':path', path)
        query.exec_()
        query.finish()

        #для имени следующей таблицы
        #self.table_count += 1
        #print(self.table_count)

    #метод чтения из базы данных
    def read_item_data(self):
        for table in self.item_data.tables():
            #print('read table', table)
            query = QtSql.QSqlQuery(self.item_data)
            query.exec('select path from {0}'.format(table))

            self.table_count += 1 #когда запускаем программу, надо, чтобы это значение было больше на 1 чем число таблиц

            if query.isActive():
                query.first()
                while query.isValid():
                    #print('after read table', query.value('path'))
                    self.create_item(query.value('path'), False)#отправляем путь в метод создания объекта модели
                    query.next()
            query.finish()

        # проверка
        for table in self.item_data.tables():
            query = QtSql.QSqlQuery(self.item_data)
            query.exec('select path, tab, tags from {0}'.format(table))
            if query.isActive():
                query.first()
                while query.isValid():
                    #print('таблица', table,'каталог', query.value('path'), 'вкладка', query.value('tab'), 'тег', query.value('tags'))
                    query.next()
            query.finish()
    #print(self.item_data.record('items').field('tab'))


    #запись тегов, теги принимаем из main_window
    def write_tags(self, tab, tags):
        print('in write tags', tags)
        c = '\n'.format(tab)
        tags = c.join(tags)
        print('tags', tags)
        for cur in self.selectionModel().selectedIndexes():
            if cur and tab: #если каталог выбран в базе #убрал проверку по тегам, чтобы можно было сбрасывать их
                #c = 'tabname:{0}:'.format(tab)
                print('cur itemd:', cur)

                a = self.model.data(cur, role=QtCore.Qt.UserRole)
                print(a)


                #i = self.model.indexFromItem(self.cur_item)
                #self.model.setData(i, path, role=QtCore.Qt.UserRole + 1)  # индекс роли - 33, в эту роль сохраняем вкладки и теги


                for table in self.item_data.tables():#просмотрели все таблицы
                    query = QtSql.QSqlQuery(self.item_data)
                    query.prepare('select path from {0} where path = (:path)'.format(table))#нашли, что в этой таблице записан путь
                                                                            #к выбранному каталогу
                    query.bindValue(':path', a)
                    query.exec_()
                    if query.isActive():
                        query.first()
                        while query.isValid():
                            print(query.value('path'))

                            #записываем вкладку
                            query_two = QtSql.QSqlQuery(self.item_data)
                            query_two.prepare('insert into {0}(tab) values(:tab)'.format(table))
                            query_two.bindValue(':tab', tab)
                            query_two.exec_()
                            query_two.finish()

                            #записываем теги
                            query_on = QtSql.QSqlQuery(self.item_data)
                            query_on.prepare('update {0} set tags = (:tags) where tab = (:tab)'.format(table))
                            query_on.bindValue(':tab', tab)
                            query_on.bindValue(':tags', tags)
                            query_on.exec_()
                            query_on.finish()

                            query.next()
                    query.finish()

    #поиск объектов по имени
    def find_item(self):
        find_color = QtGui.QBrush(QtGui.QColor(100, 100, 255))
        white = QtGui.QBrush(QtGui.QColor(255, 255, 255))

        print(self.find_line.text())
        #флаги "искать без регистра" и "искать внутри слов"
        target = self.model.findItems(self.find_line.text(), flags= QtCore.Qt.MatchFixedString|QtCore.Qt.MatchContains)
        print(target)
        #сам поиск
        for i in range(self.model.rowCount()):
            m = self.model.itemFromIndex(self.model.index(i, 0))
            if m in target and self.find_line.text():#оставляет активными только найденные объекты, все остальные делает неактивными
                #m.setEnabled(False)
              #  pass
                m.setBackground(find_color)
                self.model.insertRow(0, self.model.takeRow(i))
            else:
                m.setBackground(white)

                #m.setEnabled(True)
                #if i !=0:

    #поиск объекта по отмеченным тегам
    def find_item_tags(self, checked_tags, findTrue): #findTrue - для того, чтобы проверять, были ли отмечены теги перед запуском метода
                                                      #в случае значения False - сделает Enabled все каталоги

        find_color = QtGui.QBrush(QtGui.QColor(100,100,255))
        white = QtGui.QBrush(QtGui.QColor(255,255,255))
        temp_item_tags = {}
        true_tables = []
        true_items = []

        #попробовать пройтись по каталогам сначала в списке, попутно выбирая данные из бд смотреть в choose_item
        count = range(self.model.rowCount())

        for table in self.item_data.tables():
            query = QtSql.QSqlQuery(self.item_data)
            query.exec('select tags, tab from {0}'.format(table))
            if query.isActive():
                query.first()
                while query.isValid():
                    if query.value('tab') and query.value('tags'):  # НЕ ЗАПИСЫВАЕМ ПУСТЫЕ
                        temp_item_tags[query.value('tab')] = query.value('tags').splitlines()

                        j = 0
                        for k1 in checked_tags.keys():
                            for k2 in temp_item_tags.keys():
                                if k1 == k2:
                                    if set(checked_tags[k1]).issubset(set(temp_item_tags[k2])):
                                        # print(k1, sa[k1], k2, sb[k2])
                                        j += 1
                        # print(j)
                        if j == len(checked_tags):
                            # если есть совпадение по тегам, то добавляем в избранный список
                            true_tables.append(table)
                            #print(true_tables)
                    query.next()
            query.finish()

        for row in count:
            index_row = self.model.index(row, 0)
            item = self.model.itemFromIndex(index_row)
            path =  item.data(role = QtCore.Qt.UserRole)

            for table in true_tables:
                query = QtSql.QSqlQuery(self.item_data)
                query.exec('select path from {0}'.format(table, path))
                if query.isActive():
                    query.first()
                    while query.isValid() and query.value('path')==path:
                        print(path)
                        true_items.append(item.text())
                        query.next()
                query.finish()

            #print(true_items)

      # '''
            if item.text() not in true_items and findTrue == True:
                 #  item.setEnabled(False)
                  # if item.setBackground != white:
                 item.setBackground(white)

            elif findTrue == False:  # если не было отмеченных тегов, то восстановить все каталоги
                #item.setEnabled(True)
                item.setBackground(white)
            else:
                #item.setEnabled(True)
                item.setBackground(find_color)
                if row !=0:
                    self.model.insertRow(0, self.model.takeRow(row))
                    self.selectionModel().setCurrentIndex(self.model.index(0,0),
                                                          QtCore.QItemSelectionModel.ClearAndSelect)

    #событие закрытия окна
    def closeEvent(self, QCloseEvent):
        self.item_data.close()

if __name__ == "__main__":

    window = Item_List()
    window.setMinimumSize(300,200)
    window.show()
    sys.exit(app.exec_())