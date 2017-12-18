# -*- coding: utf8 -*-
# -*- coding: utf8 -*-

import telebot
from telebot import types
import Const
import pyodbc

bot = telebot.TeleBot(Const.MYBKBOT_TOKEN)

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
            myquery = (
            "SELECT [Table_42].[Часы за месяц] FROM [Table_42] JOIN [staff] ON ([Table_42].[Табельный номер] = [staff].[tab_number]) WHERE [staff].chat_id ='%s'" % (
            chat_id))
            cursor.execute(myquery)
            result = cursor.fetchall()
            print(result)
            for row in result:
                time = row[0]
            bot.send_message(message.from_user.id, "Вы отработали " + str(time) + " часов.")
        else:
            print("NO")
    except Exception as e:
        bot.reply_to(message, 'Вы не авторизованы, бот остановлен')

        """Просмотр всех созданных перемещений Delete=0"""


bot.polling()
