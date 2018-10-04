# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtSql, QtWidgets as QW
import sys

if __name__ == '__main__':
    app = QW.QApplication(sys.argv)


#виджет вкладок, плюс работа с чекбоксами
class TagTabs(QW.QTabWidget):

        #конструктор
        def __init__(self, parent = None):
            QW.QTabWidget.__init__(self, parent)

            #создаём таблицу
            self.setTabsClosable(True)  # кнопка закрытия на вкладке
            self.setMovable(True)  # вкладки можно перетаскивать
            self.setUsesScrollButtons(True)  # если много вкладок - кнопки прокрутки
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self.tabCloseRequested.connect(self.close_tab)  # вызывается при закрытии вкладки

            self.tab_model_dict = {}
            self.mark = True  # чтобы не отмечались флажки во время режима поиска по тегам
            self.table_count = 0  # нужен для именования таблиц

            self.connect_sql()#соединяемся с базой данных

            if __name__ =='__main__':
                #кнопка добавления вкладки
                self.vbox = QW.QHBoxLayout()
                self.vbox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)

                self.add_button = QW.QPushButton('+')
                self.vbox.addWidget(self.add_button)

                self.setLayout(self.vbox)

                self.add_button.clicked.connect(lambda: self.add_tab_dialog())


        #работа с базой данных - открытие для записи и создание вкладок, которые уже есть в базе
        def connect_sql(self):
            self.tab_data = QtSql.QSqlDatabase.addDatabase('QSQLITE', connectionName = 'tabs')  # указываем тип базы данных, QSQLITE для базы типа sqlite3
            self.tab_data.setDatabaseName('data//tab_data')  # имя базы или путь до неё
            self.tab_data.open()
           # self.tab_data = tab_data
            print('существующие таблицы: ', self.tab_data.tables())
            self.read_tabs_from_sql()#восстанавливаем созданные вкладки

        # метод восстановления вкладок из базы данных
        def read_tabs_from_sql(self):
            for tab in self.tab_data.tables():
                print('in read tab sql', tab)
                model = QtGui.QStandardItemModel()
                name =''

                query = QtSql.QSqlQuery(self.tab_data)
                query.exec('select name from {0}'.format(tab))

                if query.isActive():
                    query.first()
                    while query.isValid() and query.value('name'):
                        name = query.value('name')
                        print('value name', query.value('name'))
                        query.next()
                query.finish()

                self.add_new_tab(name, model)
                self.read_tags_from_sql(tab, model)


        #добавление тэгов из бд
        def read_tags_from_sql(self, tab_name, model):#к восстановленным вкладкам добавляем теги
            #print(tab_name)
            query = QtSql.QSqlQuery(self.tab_data)
            query.exec('select tags from {0}'.format(tab_name))
            if query.isActive():  # проверяем, что запрос активен
                query.first()  # установили указатель
                while query.isValid():  # проверяем, что поле не пустое
                    print('in read tags sql',query.value('tags'))
                    if query.value('tags'):
                        self.new_checkbox_by_name(query.value('tags'), model, False)#tags - поле для тэгов в каждой таблице, сохраняющей вкладку
                    query.next()  # переходим к следующей записи в запросе

            query.finish()

        # создание таблицы для хранения информации о вкладках
        def write_tab_sql(self, tab_name):
            t_name = '_' + str(self.table_count) + '_'
            print('t_name',t_name)
            while True:
                if t_name in self.tab_data.tables():
                    self.table_count += 1
                    t_name = '_' + str(self.table_count) + '_'
                else:
                    break

            if t_name not in self.tab_data.tables():
                print('создаём таблицу: ', tab_name)
                query = QtSql.QSqlQuery(self.tab_data)  # объект запроса
                #tags - единственная колонка, одинакова во всех таблицах
                query.exec('create table {0}(name text COLLATE NOCASE, tags text COLLATE NOCASE)'.format(t_name))
                query.finish()

                query = QtSql.QSqlQuery(self.tab_data)  # объект запроса
                query.prepare('insert into {0}(name) values(:name)'.format(t_name))
                query.setForwardOnly(True)
                query.bindValue(":name", tab_name)
                print('tab name',tab_name)
                query.exec_()
                query.finish()

                #проверка
            '''
            for t in self.tab_data.tables():
                query = QtSql.QSqlQuery(self.tab_data)
                query.exec('select name from {0}'.format(t))
                print('проверка', t)
                if query.isActive():
                    query.first()
                    while query.isValid():
                        print('value name', query.value('name'))
                        query.next()
                query.finish()
                '''



        #сохраняем записанные в текущую вкладку тэги в базу данных
        def write_checkbox_sql(self, checkbox_name, tab_name): #ДОБАВИТЬ ПРОВЕРКУ НА СУЩЕСТВУЮЩЕЕ ЗНАЧЕНИЕ!!!
            print('in write chbx sql')

            cur_table = self.define_cur_table(tab_name)

            print(cur_table)
            query = QtSql.QSqlQuery(self.tab_data)  # объект запроса
            # запрос с получаемыми параметрами
            print(checkbox_name)
            query.prepare('insert into {0}(tags) values(:tag)'.format(cur_table))  # данный метод используется, если в запрос нужно передать параметры
            query.setForwardOnly(True)  # задаём перемещение от начала к концу, якобы для экономии ресурсов...
            query.bindValue(':tag', checkbox_name)  # метод на странице 606, вставляет значение в следующее поле при каждом вызове
            query.exec_()  #выполнение подготовленного запроса
            query.finish()

            print(
                query.lastError().text())  # выведет текст ошибки при повторяющемся значении, т.к. в поле tag указано unique
            if query.lastError().isValid(): print('error')  # работает
            if query.lastError().type() == QtSql.QSqlError.TransactionError: print('error type')
            print(query.lastError().type())  # ошибка №1 - ошибка с соединением с базой

        #удаление тэга из таблицы
        @QtCore.pyqtSlot()
        def delete_tag_sql(self, tab_name, checkbox_name):
            cur_table = self.define_cur_table(tab_name)

            print(tab_name, checkbox_name)
            query = QtSql.QSqlQuery(self.tab_data)  # объект запроса
            query.prepare('delete from {0} where tags = (:tag)'.format(cur_table))  # данный метод используется, если в запрос нужно передать параметры
            query.setForwardOnly(True)  # задаём перемещение от начала к концу, якобы для экономии ресурсов...
            query.bindValue(':tag', checkbox_name)  # метод на странице 606, вставляет значение в следующее поле при каждом вызове
            query.exec_()  # выполнение подготовленного запроса
            query.finish()
            query.exec('VACUUM')
            query.finish()

        #находим таблицу в базе данных соответствующую вкладке
        def define_cur_table(self, tab_name):
            cur_tab = ''
            for t in self.tab_data.tables():
                query = QtSql.QSqlQuery(self.tab_data)  # объект запроса
                query.exec('select name from {0}'.format(t))
                if query.isActive():
                    query.first()
                    while query.isValid():
                        if tab_name == query.value('name'):
                            cur_tab = t
                            break
                        query.next()
                query.finish()
            return cur_tab

        #удаление таблицы
        def delete_tab_sql(self, tab_name):
            for_del = self.define_cur_table(tab_name)
            query = QtSql.QSqlQuery(self.tab_data)  # объект запроса
            query.exec('drop table {0}'.format(for_del))
            query.finish()
            query.exec('VACUUM')
            query.finish()

            self.tab_model_dict.pop(tab_name)#удаляем из словаря вкладка:модель
            #print(self.tab_model_dict)

        #диалог добавления новой вкладки
        #@QtCore.pyqtSlot()
        def add_tab_dialog(self):
            # проще так, чем отдельным классом окна
            tab_dialog = QW.QInputDialog(self)  # диалоговое окно для ввода имени вкладки
            tab_dialog.setWindowModality(QtCore.Qt.ApplicationModal)  # блокирует все окна приложения
            tab_dialog.resize(400, 80)
            tab_dialog.setWindowTitle(' ')
            tab_dialog.setLabelText('Enter tab name: ')

            model = QtGui.QStandardItemModel()#модель задаём тут, чтобы можно было указывать модель, когда добавляем чекбоксы из бд
            tab_dialog.textValueSelected.connect(lambda: self.add_new_tab(tab_dialog.textValue(), model, new = True))  # сигнал при нажатии кнопки OK
            tab_dialog.exec_()  # запуск цикла диалогового окна

        #метод добавления вкладки
        def add_new_tab(self, tab_name, model, new = False):#теперь этот метод более универсален, так как тип модели передаём в параметрах
            print('in add new tab', tab_name)
            tab_names = []

            if new:
                for t in self.tab_data.tables():
                    query = QtSql.QSqlQuery(self.tab_data)
                    query.exec('select name from {0}'.format(t))

                    if query.isActive():
                        query.first()
                        while query.isValid():
                            tab_names.append(query.value('name'))
                            query.next()
                    query.finish()

            print('tab names',tab_names)
            # режим выделения с Ctrl

            if tab_name not in tab_names:  # проверяем, что нет вкладки с таким же именем
                self.table_count += 1

                #строка ввода
                line_add_tag = QW.QLineEdit()
                validator = QtGui.QRegExpValidator(QtCore.QRegExp('\w{1,}.{0,}'))  # обязательна буква или цифра
                # от ноля и больше вхождения любого символа, но минимум одна буква или цифра
                line_add_tag.setValidator(validator)#добавили валидатор по созданному регулярному выражению
                line_add_tag.setPlaceholderText("<Enter tag's name here>")  # замещающий текст

                #тэги будем представлять в виде списка
                tag_list = QW.QListView()
                #model = QtGui.QStandardItemModel()#модель задаём в параметрах
                tag_list.setModel(model)
                tag_list.setSelectionMode(QW.QAbstractItemView.ExtendedSelection)#режим множественного выделения, с ctrl и областью
                tag_list.setResizeMode(QW.QListView.Adjust)#подгоняем размещение элементов под размер списка
                tag_list.setFlow(QW.QListView.LeftToRight)#направление вывода
                tag_list.setWrapping(True)#перенос элементов на новую строку разрешён
                tag_list.setWordWrap(True)#перенос текста элементов на новую строку разрешён
                #tag_list.setUniformItemSizes(True)
                width_size = QtCore.QSize(200,30)
                tag_list.setGridSize(width_size)#задаём размеры таблицы размещения, 200 - макс. длина строки до
                #обрезки текста, 30 - отступ между строками по вертикали
                #скрыть первую строку


                #tag_list.setMovement(QW.QListView.Free)#почему-то дублирует перетаскиваемый объект
                #model.itemChanged.connect(lambda:print('asdasd'))#сигнал о том, что какой-то элемент был изменён
                #надо установить валидатор...

                #слой для строки ввода и тэгов
                vb = QW.QVBoxLayout()
                vb.setAlignment(QtCore.Qt.AlignTop)
                #vb.addLayout(hb)
                vb.addWidget(line_add_tag)
                vb.addWidget(tag_list)


                #btn_plus.clicked.connect(lambda: self.valid_checkbox_name(line_add_tag.text(), line_add_tag, model))
                #btn_delete.clicked.connect(lambda: self.delete_checkbox_by_name(model))
                #btn_appoint.clicked.connect(lambda: QtCore.QCoreApplication.sendEvent(item_list.Item_List(), Mid()))


                #контейнер - обязательно виджет, гроупбокс или подобное
                tag_group = QW.QWidget()
                tag_group.setLayout(vb)



                #не нужна в связи с переходом на представление в виде списка
                #scrollArea = QW.QScrollArea()
                #scrollArea.setWidget(tag_group)#вставили контейнер с сеткой
                #scrollArea.setWidgetResizable(True)#без этого сетка с множеством компонентов тупо сжимается
                #scrollArea.ensureWidgetVisible(line_add_tag)

                #сигналы
                line_add_tag.returnPressed.connect(
                    lambda: self.valid_checkbox_name(line_add_tag.text(), line_add_tag, model))  # вызывается при нажатии Enter

                self.addTab(tag_group, tab_name)#
                self.setCurrentIndex(self.count()-1)  # автоматически переключаемся на созданную вкладку

                t_name = '_' + str(self.table_count) + '_'
                self.tab_model_dict[tab_name] = (model, tag_list.selectionModel())#для того, чтобы можно было удалять теги из модели во вкладке
                #print(self.tab_model_dict)
                #будем удалять из model тот чекбокс, который выделен в selectionModel

                #записываем вкладку в базу данных:
                if new:
                    print("write_tab_sql from add tab")
                    self.write_tab_sql(tab_name)

            else:
                print('вкладка с таким именем уже существует! добавить диалог с ошибкой')


        #обработчик сигнала закрытия вкладки
        def close_tab(self, index):
            #key = self.tabText(index)
            #print(key)
            #selectionBehaviorOnRemove - поведение при закрытии вкладки, на какую переключиться
            self.delete_tab_sql(self.tabText(index))
            self.removeTab(index)


       # добавим чекбокс, для которого введено имя в строку и нажат enter
        def valid_checkbox_name(self, text, line, model):
            if line.hasAcceptableInput():#проверка ввода по валидатору
                line.clear()  # очистили строку ввода
                line.setPlaceholderText("<Enter tag's name here>")  # замещающий текст
                line.setFocus()

                #решаем проблему с одинаковыми именами тегов в одной вкладке
                exists = []
                for i in range(model.rowCount()):
                    exists.append(model.item(i).text())
                if text not in exists:
                    self.new_checkbox_by_name(text, model, True)#основной метод создания чекбокса, разбил исходный метод на 2,
                                                      #чтобы напрямую добавлять чекбоксы из базы данных
        #метод прямого создания чекбокса
        def new_checkbox_by_name(self, text, model, from_line):
            item = QtGui.QStandardItem(text)
            item.setCheckable(True)
            item.setEditable(False)  # пока не будем разрешать редактировать текст тега
            model.appendRow(item)
            #item.setIcon(QtGui.QIcon('icons/icon.png'))
            #запись в бд
            if from_line:#чтобы не было повторного вызова при чтении из бд
                #то есть только если создаём чекбокс из введёного в строку текста
                self.write_checkbox_sql(text, self.tabText(self.currentIndex()))

        # указываем модель из текущей вкладки
        @QtCore.pyqtSlot()
        def change_checkbox(self):
            name = self.tabText(self.currentIndex())
            model = self.tab_model_dict[name][0]
            select_model = self.tab_model_dict[name][1]
            self.delete_checkbox_by_name(model, select_model)

        # удаляем выделенные чекбоксы
        @QtCore.pyqtSlot()
        def delete_checkbox_by_name(self, model, select_model):
            for index in select_model.selectedIndexes():
                #print(index)
                if select_model.isSelected(index):

                    # удаление из бд
                    self.delete_tag_sql(self.tabText(self.currentIndex()), model.itemFromIndex(index).text())

                    model.removeRow(index.row())
                    self.delete_checkbox_by_name(model, select_model)

        #назначение тегов папкам
        @QtCore.pyqtSlot()
        def app_checkbox_to_folder(self):
            name = self.tabText(self.currentIndex())
            model = self.tab_model_dict[name][0]

            tags = []

            for index in range(model.rowCount()):
                if model.item(index):  # по указанному индексу есть элемент
                    if model.item(index).checkState() == QtCore.Qt.Checked:
                        print(model.item(index).text())
                        tags.append(model.item(index).text())
            #print(tags)
            return name, tags

        @QtCore.pyqtSlot()#отмечаем чекбоксы, сохранённые в item_data при выборе папки из списка
        def mark_checkbox(self, temp_tab_tags):

            #сбрасываем все флажки в самом начале:
            for tab_index in range(self.count()):#перебрали все вкладки
                name = self.tabText(tab_index)
                model = self.tab_model_dict[name][0]#нашли модель
                for index in range(model.rowCount()):#перебрали все теги в каждой
                    if model.item(index):  # нашли тег
                        model.item(index).setCheckState(QtCore.Qt.Unchecked)  #сброс флажка

            tabs = temp_tab_tags.keys()
            #tags = temp_tab_tags.values()
            #print(tabs, tags)

            for temp_tab in tabs:
                for tab_index in range(self.count()):#количество вкладок
                    if temp_tab == self.tabText(tab_index): #если вкладка из словаря найдена

                        name = self.tabText(tab_index)
                        print('mark', name)
                        model = self.tab_model_dict[name][0]#нашли модель

                        for index in range(model.rowCount()):
                            if model.item(index) and model.item(index).text() in temp_tab_tags[temp_tab]:#нашли тег
                                #print(model.item(index).text())
                                if self.mark:
                                    model.item(index).setCheckState(QtCore.Qt.Checked)#отметили его!

        #метод поиска папок по совпадению с отмеченными элементами
        def find_item_by_tag(self):
            checked_tags = {}
            for tab_index in range(self.count()):

                name = self.tabText(tab_index)
                model = self.tab_model_dict[name][0]
                tags = []

                for index in range(model.rowCount()):
                    if model.item(index):  # по указанному индексу есть элемент
                        if model.item(index).checkState() == QtCore.Qt.Checked:
                            #print(model.item(index).text())
                            tags.append(model.item(index).text())
                            #print('sssssssssss',tags)
                if tags: checked_tags[name] = tags #записываем только вкладки с тегами

            #print(checked_tags)
            return checked_tags


        #событие закрытия окна
        def closeEvent(self, QCloseEvent):
            self.tab_data.close()


#если запускаем как самостоятельный модуль
if __name__ == '__main__':

    tagMakerWindow = TagTabs()
    tagMakerWindow.setMinimumSize(300,200)
    tagMakerWindow.show()
    sys.exit(app.exec_())
