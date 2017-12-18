# -*- coding: utf8 -*-
# -*- coding: utf8 -*-

import telebot
from telebot import types
import Const
import pyodbc
import logging
import time

bot = telebot.TeleBot(Const.API_TOKEN)

user_dict = {}


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.unit = None
        self.yes = None


@bot.message_handler(commands=["start"])
def geophone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(button_phone)
    msg = bot.send_message(message.chat.id,
                           "Для работы со мной необходима авторизация. Отправь мне свой номер телефона.",
                           reply_markup=keyboard)
    bot.register_next_step_handler(msg, process_phone_step)
    print(message.contact)
    """Начало авторизации пользователя"""


def process_phone_step(message):
    try:
        phone_user = message.contact.phone_number
        s = phone_user
        if s[0] == '+':
            s = s[1:len(s)]
        print(s)
        '#Начало проверки пользователя в БД, если пользователь не найден - функция не выполняется'
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 13 for SQL Server};SERVER=DESKTOP-9OO0O0I\SQLEXPRESS;DATABASE=test;UID=sa;PWD=Abc12345')
        cursor = cnxn.cursor()
        myquery = ("select * from staff WHERE phone = '%s'" % s)
        cursor.execute(myquery)
        result = cursor.fetchall()
        for row in result:
            name_number = row[1]
            phone_number = row[3]
            print(phone_number)
            chat_id2 = message.chat.id
            cnxn = pyodbc.connect(
                'DRIVER={ODBC Driver 13 for SQL Server};SERVER=DESKTOP-9OO0O0I\SQLEXPRESS;DATABASE=test;UID=sa;PWD'
                '=Abc12345')
            cursor = cnxn.cursor()
            myquery_unit = ("update staff set chat_id =%s WHERE phone =%s" % (chat_id2, phone_number))
            cursor.execute(myquery_unit)
            cnxn.commit()
            print(phone_number)
            bot.reply_to(message, "Здравствуйте, " + name_number + "\nДанные обновлены, бот включен")
    except Exception as e:
        print("К сожалению такой номер не найден, бот выключен.")
        bot.reply_to(message, "К сожалению такой номер не найден, бот выключен.")

        """Ожидание ввода номера телефона, авторизация бота"""


@bot.message_handler(commands=['add'])
def send_welcome(message):
    try:
        chat_id = message.chat.id
        print(chat_id)
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 13 for SQL Server};SERVER=DESKTOP-9OO0O0I\SQLEXPRESS;DATABASE=test;UID=sa;PWD=Abc12345')
        cursor = cnxn.cursor()
        myquery = ("select chat_id from staff WHERE chat_id =%s" % (chat_id))
        cursor.execute(myquery)
        result = cursor.fetchall()
        print(result)
        for row in result:
            chat_i = row[0]
            print(chat_i)
        if str(chat_i) == str(chat_id):
            msg = bot.reply_to(message, "Откуда забираем? Введи номер ресторана")
            bot.register_next_step_handler(msg, process_name_step)
        else:
            print("No")
    except Exception as e:
        bot.send_message(message.chat.id,
                         "Вы не авторизованы, бот остановлен")
        """Функция перемещения между ресторанами"""


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, "Что забираем? Введи товар и количество, например: Помидоры 2 кейса")
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        print("Ooops")
        """Функция ввода продукта"""


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        user = user_dict[chat_id]
        user.age = age
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 13 for SQL Server};SERVER=DESKTOP-9OO0O0I\SQLEXPRESS;DATABASE=test;UID=sa;PWD=Abc12345')
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO product (id, unit, comment, deleted) VALUES (?, ?, ?, 0)",
                       (chat_id, user.name, user.age))
        cnxn.commit()
        bot.reply_to(message, 'Данные успешно добавлены')
    except Exception as e:
        bot.reply_to(message, 'oooops')
        """Добавление записи в БД - перемещение"""


@bot.message_handler(commands=['allunit'])
def send_welcome(message):
    try:
        chat_id = message.chat.id
        print(chat_id)
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 13 for SQL Server};SERVER=DESKTOP-9OO0O0I\SQLEXPRESS;DATABASE=test;UID=sa;PWD=Abc12345')
        cursor = cnxn.cursor()
        myquery = ("select chat_id from staff WHERE chat_id =%s" % (chat_id))
        cursor.execute(myquery)
        result = cursor.fetchall()
        print(result)
        for row in result:
            chat_i = row[0]
            print(chat_i)
        if str(chat_i) == str(chat_id):
            cnxn = pyodbc.connect(
                'DRIVER={ODBC Driver 13 for SQL Server};SERVER=DESKTOP-9OO0O0I\SQLEXPRESS;DATABASE=test;UID=sa;PWD=Abc12345')
            cursor = cnxn.cursor()
            myquery = ("SELECT * FROM product WHERE deleted = 0")
            cursor.execute(myquery)
            result = cursor.fetchall()
            for row in result:
                id = row[3]
                unit = row[1]
                comment = row[2]
                all = str(row[1]) + str(row[2])
                print(str(unit))
                bot.send_message(message.from_user.id, "Мы должны ресторану № " + str(unit) + "\nТовар: " + str(
                    comment) + "\nИдентификатор:" + str(id))
        else:
            print("NO")
    except Exception as e:
        bot.reply_to(message, 'Вы не авторизованы, бот остановлен')

        """Просмотр всех созданных перемещений Delete=0"""


@bot.message_handler(commands=['return'])
def send_welcome(message):
    try:
        chat_id = message.chat.id
        print(chat_id)
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 13 for SQL Server};SERVER=DESKTOP-9OO0O0I\SQLEXPRESS;DATABASE=test;UID=sa;PWD=Abc12345')
        cursor = cnxn.cursor()
        myquery = ("select chat_id from staff WHERE chat_id =%s" % (chat_id))
        cursor.execute(myquery)
        result = cursor.fetchall()
        print(result)
        for row in result:
            chat_i = row[0]
            print(chat_i)
        if str(chat_i) == str(chat_id):
            msg = bot.reply_to(message, "Для удаления перемещения введите идентификатор")
            bot.register_next_step_handler(msg, process_return_step)
        else:
            print("NO")
    except Exception as e:
        bot.send_message(message.chat.id,
                         "Вы не авторизованы, бот остановлен")


def process_return_step(message):
    try:
        unit = message.text
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 13 for SQL Server};SERVER=DESKTOP-9OO0O0I\SQLEXPRESS;DATABASE=test;UID=sa;PWD=Abc12345')
        cursor = cnxn.cursor()
        myquery_unit = ("update product set deleted = 1 WHERE num = '%s'" % unit)
        cursor.execute(myquery_unit)
        cnxn.commit()
        bot.reply_to(message, 'Перемещение удалено')
    except Exception as e:
        bot.reply_to(message, 'Перемещение с таким идентификатором не найдено')
        """Удаление перемещения из БД Delete = 1"""


while True:

    try:

        bot.polling(none_stop=True)

    except Exception as err:

        logging.error(err)

        time.sleep(5)

        bot.send_message(242962445, "Проблемы с интернетом, нужна перезагрузка")
