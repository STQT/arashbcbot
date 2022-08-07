import logging
import time
import telebot
import configs

from aiogram.utils import executor
from aiogram.utils.executor import start_webhook

from aiogram import Dispatcher, Bot, types
from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery,
                           InputMediaPhoto,
                           ReplyKeyboardMarkup)

from configs import TOKEN
import sqlite3

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

connection = sqlite3.connect('data.sqlite', check_same_thread=False)

cursor = connection.cursor()


def get_planirovka():
    """Получить все категории товаров"""
    query = cursor.execute("SELECT planirovka FROM planirovka LIMIT 5;").fetchall()
    categories = []
    for i in query:
        categories.append(i[0])
    return categories


async def get_galereyas():
    """Получить все категории товаров"""
    query = cursor.execute("SELECT galereya FROM galereya LIMIT 8;").fetchall()
    komnatas = []
    for i in query:
        komnatas.append(i[0])
    return komnatas


async def user_id_registration(tg_id, tg_username):
    telegram_user_id = cursor.execute(f"SELECT telegram_id FROM users WHERE telegram_id LIKE {tg_id};").fetchone()
    if telegram_user_id is None:
        sql = f"INSERT INTO users (telegram_id, username, checking) VALUES ({tg_id}, '{str(tg_username)}', 1)"
        cursor.execute(sql)  # aaa
        connection.commit()
    else:
        sql = f"Update users set checking = 1 where telegram_id = {tg_id}"
        cursor.execute(sql)
        connection.commit()


async def get_active_users():
    telegram_user_id = cursor.execute("SELECT telegram_id FROM users WHERE checking LIKE 1").fetchall()
    return telegram_user_id


@dp.message_handler(lambda msg: msg.text == "🔙На главную" or msg.text == "/start")
async def send_welcome_homepage(message):
    await user_id_registration(message.from_user.id, message.from_user.username)
    first_name = message.from_user.first_name
    markup = ReplyKeyboardMarkup()
    markup.add('🖼Галерея')
    markup.add('🏢Планировки', '🔸Акции и бонусы')
    markup.add('📂Скачать каталог')
    markup.add('❔О Бизнес центре', '📞Связаться с нами')
    markup.add('👥Обслуживание клиентов')
    if message.from_user.id == 986262919 or message.from_user.id == 29895715 or message.from_user.id == 390736292:
        markup.add('Администрирование')
    await bot.send_message(message.chat.id, f"Здравствуйте, *{first_name}*!\nВыберите нужный раздел 👇 ",
                           reply_markup=markup,
                           parse_mode="Markdown")


@dp.message_handler(commands=["addtolist"])
async def addtolist(message):
    if message.from_user.id == 986262919 or message.from_user.id == 29895715 or message.from_user.id == 390736292:
        strings = message.text.split()
        if len(strings) >= 4:
            strings.remove('/addtolist')
            str1 = ' '.join(str(x) for x in strings[2:])
            # Connecting to the SQL database

            try:
                cursor.execute("INSERT INTO clients VALUES('" + strings[0] + "','" + strings[
                    1] + "','" + str1 + "', 'NULL', 'NULL')")
                await bot.reply_to(message,
                                   f"✅Добавлен: \nДоговор: {strings[0]},\nСрок: {strings[1]},\nНазвание: {str1}")
                connection.commit()

            except Exception as e:
                await bot.reply_to(message, "Внутрення ошибка бота либо этот номер договора уже есть! Код ошибки:")
                await bot.send_message(message, e)
        else:
            await bot.send_message(message.chat.id, "Вы ничего не ввели или неверно введено")

    else:
        await bot.send_message(message.from_user.id, "Вы не имеете доступ к этой команде!")


@dp.message_handler(commands=["getlist"])
async def getlist(message):
    if message.from_user.id == 986262919 or message.from_user.id == 29895715 or message.from_user.id == 390736292:
        try:
            cursor.execute("SELECT * FROM clients")
            firmalar = cursor.fetchall()
            for row in firmalar:
                if row[3] != 'NULL':
                    await bot.send_message(message.chat.id,
                                           f"Договор = {row[0]} Срок = {row[1]} Фирма: {row[2]}, пользователь: @{row[3]}")
                else:
                    await bot.send_message(message.chat.id,
                                           f"Договор = {row[0]} Срок = {row[1]} Фирма: {row[2]}, не авторизован")
        except Exception as e:
            await bot.send_message(message.chat.id, "Нет соединения с базой данных\n"
                                                    f"{e}")
    else:
        await bot.send_message(message.from_user.id, "Вы не имеете доступ к этой команде!")


@dp.message_handler(commands=["delete"])
async def deleteitem(message):
    if message.from_user.id == 986262919 or message.from_user.id == 29895715 or message.from_user.id == 390736292:
        strings = message.text.split()
        if len(strings) >= 3:
            strings.remove('/delete')

            # Connecting to the SQL database

            try:
                client_ids = int(strings[0])
                sroks = strings[1]

                cursor.execute(f"DELETE FROM clients WHERE client_id = {client_ids} AND srok = '{sroks}'")
                await bot.reply_to(message, f"Договор под номером {client_ids} был успешно удален ")
                connection.commit()

            except Exception as e:
                await bot.reply_to(message, "Внутрення ошибка бота, повторите команду:")
                await bot.send_message(message.from_user.id, e)

        else:
            await bot.send_message(message.chat.id, "Вы ничего не ввели или неверно введено")

    else:
        await bot.send_message(message.from_user.id, "Вы не имеете доступ к этой команде!")


@dp.message_handler(commands=["opros"])
async def oprosadd(message):
    if message.from_user.id == 986262919 or message.from_user.id == 29895715 or message.from_user.id == 390736292:
        strings = message.text.split()
        if len(strings) >= 2:
            strings.remove('/opros')
            # Connecting to the SQL database
            try:
                links = strings[0]
                sql = '''UPDATE opros
                                            SET link = ?
                                            WHERE id_link = ?'''
                cursor.execute(sql, (links, 1)).fetchone()
                connection.commit()
                await bot.reply_to(message, f"Ссылка: {links} был успешно добавлен в опросник!")
            except Exception as e:
                await bot.reply_to(message, "Внутрення ошибка бота, код ошибки:")
                await bot.send_message(message.from_user.id, e)

        else:
            await bot.send_message(message.chat.id, "Вы ничего не ввели или неверно введено")

    else:
        await bot.send_message(message.from_user.id, "Вы не имеете доступ к этой команде!")


'''Администрирование'''


@dp.message_handler(lambda msg: msg.text == "Администрирование")
async def administrirovaniye(msg):
    markup = ReplyKeyboardMarkup()
    markup.add('Отправить пост')
    markup.add('Галерея')
    markup.add('Планировки', 'Акции и бонусы')
    markup.add('Скачать каталог')
    markup.add('Нам доверяют', 'Связаться с нами')
    markup.add('Преимущества')
    message = 'Для добавление договора напишите: /addtolist <nomer dogovora> <srok> <nazvaniye>\n\n' \
              'Для просмотра всех договоров в базе напишите: /getlist \n' \
              'Для удаления договора с базы напишите: /delete <nomer dogovora> <srok>' \
              'Для добавления ссылки в опросник напишите: /opros <ссылка на опрос>'
    await bot.send_message(msg.from_user.id, message, reply_markup=markup)


admin_dict = {}
n = 1


@dp.message_handler(lambda msg: msg.text == "Галерея")
async def get_list_galereya_admin(message):
    galereyas = get_galereyas()
    keyboard = ReplyKeyboardMarkup()
    for galereya in galereyas:
        keyboard.add(f'{galereya}')
    keyboard.add('🔙На главную')
    msg = await bot.send_message(message.from_user.id, 'Выбери из списка название раздела', reply_markup=keyboard)
    await bot.register_next_step_handler(msg, get_name_galereya_admin)


async def get_name_galereya_admin(message):
    try:
        if message.text == u'🔙На главную':
            raise Exception('Отмена регистрации')
        name = message.text
        telegram_id = message.from_user.id
        admin_dict[telegram_id] = n
        admin_dict['name'] = name
        msg = await bot.send_message(message.chat.id, 'Отправь мне файлы без сжатия (макс 500кб).'
                                                      ' И когда надо остановиться жми /submit', )
        await bot.register_next_step_handler(msg, get_file_galereya_admin)

    except Exception as ex:
        if ex.args == ('Отмена регистрации',):
            await send_welcome_homepage(message)

        await bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


async def get_file_galereya_admin(message):
    text = admin_dict['name']

    try:
        if message.text == u'🔙На главную':
            raise Exception('Отмена регистрации')
        elif message.text != '/submit':
            if message.document:
                save_dir = 'media'
                file_name = message.document.file_name
                file_id_info = await bot.get_file(message.document.file_id)
                downloaded_file = await bot.download_file(file_id_info.file_path)
                src = file_name

                with open(save_dir + "/" + src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                cursor.execute(
                    f"UPDATE galereya SET pic{admin_dict[message.from_user.id]} = "
                    f"'{str(file_name)}' WHERE galereya = '{text}'").fetchone()
                connection.commit()
                msg = bot.send_message(message.chat.id,
                                       "[*] Файл № {} добавлен:\nИмя файла - {}\nОтправь мне {} - фото\n"
                                       "Либо нажми на /submit".format(
                                           admin_dict[message.from_user.id], str(file_name),
                                           admin_dict[message.from_user.id] + 1))

                if admin_dict[message.from_user.id] == 10:
                    return await bot.send_message(message.chat.id,
                                                  "Поздравляем ты дошел до предела! Нажми На главную или на /start")

                bot.register_next_step_handler(msg, get_file_galereya_admin)
                admin_dict[message.from_user.id] += 1
            else:
                msg = bot.send_message(message.chat.id,
                                       f"Пожалуйста отправь мне сжатый изображение\nСейчас ты отправишь мне {n}-фото")
                bot.register_next_step_handler(msg, get_file_galereya_admin)
        else:
            for i in range(admin_dict[message.from_user.id], 11):
                cursor.execute(
                    f"UPDATE galereya SET pic{i} = NULL WHERE galereya = '{text}'").fetchone()
            connection.commit()
            await bot.send_message(message.chat.id, f"Добавлено {admin_dict[message.from_user.id] - 1} фото!")

    except Exception as ex:
        if ex.args == ('Отмена регистрации',):
            await send_welcome_homepage(message)

        await bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


@dp.message_handler(lambda msg: msg.text == "Отправить пост")
async def get_sms_admin(message):
    msg = await bot.send_message(message.chat.id, 'Отправь мне сообщение')  # noqa
    bot.register_next_step_handler(message, get_answer_photo)


async def get_answer_photo(message):
    if message.photo:
        photo = bot.get_file(message.photo[2].file_id)
        sql = """UPDATE post SET img = ?, text = ?  WHERE id = 1"""
        cursor.execute(sql, (str(photo.file_path), str(message.caption),)).fetchone()
        connection.commit()
        downloaded_file = bot.download_file(photo.file_path)
        await bot.send_photo(message.chat.id, downloaded_file, message.caption)
        markup = ReplyKeyboardMarkup()
        markup.add('Да! Фото')
        markup.add('Нет!')
        await bot.send_message(message.chat.id, "Правильно ввёл?",
                               reply_markup=markup)
        bot.register_next_step_handler(message, get_sms_text_admin)
    elif message.text:
        await bot.send_message(message.chat.id, message.text)
        sql = """UPDATE post SET text = ? WHERE id = 1"""
        cursor.execute(sql, (str(message.text),)).fetchone()
        connection.commit()
        markup = ReplyKeyboardMarkup()
        markup.add('Да! Текст')
        markup.add('Нет!')
        await bot.send_message(message.chat.id, "Правильно ввёл?",
                               reply_markup=markup)
        bot.register_next_step_handler(message, get_sms_text_admin)
    else:
        await bot.send_message(message.chat.id, "Только работает с фото и текстом")
        bot.register_next_step_handler(message, get_answer_photo)


async def get_sms_text_admin(message):
    query = cursor.execute("SELECT * FROM post;").fetchone()
    users = get_active_users()
    if message.text == 'Да! Фото':
        for send in users:
            downloaded_file = bot.download_file(query[0])
            try:
                await bot.send_photo(send[0], downloaded_file, query[1])
            except Exception as e:
                logging.warning("Error checking user active: %s", e)
                sql = """Update users set checking = ? where telegram_id = ?;"""
                cursor.execute(sql, (0, send[0])).fetchone()
                connection.commit()
                await bot.send_message(message.chat.id, f"net takogo id {send[0]}")
            time.sleep(0.03)
        await send_welcome_homepage(message)
    elif message.text == 'Да! Текст':
        for send in users:
            try:
                await bot.send_message(send[0], query[1])
            except Exception as e:
                logging.warning("Error sending message: %s", e)
                sql = """Update users set checking = ? where telegram_id = ?;"""
                cursor.execute(sql, (0, send[0])).fetchone()
                connection.commit()
                await bot.send_message(message.chat.id, f"net takogo id {send[0]}")
            time.sleep(0.03)
        await send_welcome_homepage(message)
    elif message.text == 'Нет!':
        await bot.send_message(message.chat.id, "Повторно отправьте сообщение")
        bot.register_next_step_handler(message, get_answer_photo)


@dp.message_handler(lambda msg: msg.text == "Планировки")
async def get_list_planirovka_admin(message):
    planirovkas = get_planirovka()
    keyboard = ReplyKeyboardMarkup()
    for planirovka in planirovkas:
        keyboard.add(f'{planirovka}')
    keyboard.add('🔙На главную')
    msg = await bot.send_message(message.from_user.id, 'Выбери из списка название раздела', reply_markup=keyboard)
    bot.register_next_step_handler(msg, get_name_planirovka_admin)


async def get_name_planirovka_admin(message):
    name = message.text
    admin_dict['planirovka'] = name
    msg = await bot.send_message(message.chat.id, 'Отправь мне файлы без сжатия (макс 500кб).')
    bot.register_next_step_handler(msg, get_file_planirovka_admin)


async def get_file_planirovka_admin(message):
    text = admin_dict['planirovka']
    try:
        if text == u'🔙На главную':
            raise Exception('Отмена регистрации')
        if message.document:
            save_dir = 'media'
            file_name = message.document.file_name
            file_id_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)
            src = file_name

            with open(save_dir + "/" + src, 'wb') as new_file:
                new_file.write(downloaded_file)
            cursor.execute(
                f"UPDATE planirovka SET pic1 = '{message.document.file_id}' WHERE planirovka = '{text}'").fetchone()
            connection.commit()

            await bot.send_message(message.chat.id,
                                   "[*] Файл добавлен:\nИмя файла - {}\n".format(str(file_name)))
            administrirovaniye(message)

        else:
            await bot.send_message(message.chat.id,
                                   f"Пожалуйста отправь мне сжатый изображение\nСейчас ты отправишь мне {n}-фото")
    except Exception as ex:
        print(ex)
        if ex.args == ('Отмена регистрации',):
            send_welcome_homepage(message)

        await bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


@dp.message_handler(lambda msg: msg.text == "Скачать каталог")
async def get_catalogue_admin(message):
    msg = await bot.send_message(message.from_user.id, 'Отправь мне файл или сообщение')
    bot.register_next_step_handler(msg, get_catalogue_text_admin)


async def get_catalogue_text_admin(message):
    try:
        if message.document:
            save_dir = 'media'
            file_name = message.document.file_name
            file_id_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)
            src = file_name

            with open(save_dir + "/" + src, 'wb') as new_file:
                new_file.write(downloaded_file)
            cursor.execute(f"UPDATE texts SET text = 'file! {str(file_name)}' WHERE menu = 'Katalog'").fetchone()
            connection.commit()
            await bot.send_message(message.chat.id,
                                   "[*] File added:\nFile name - {}\nFile directory - {}".format(str(file_name),
                                                                                                 str(save_dir)))
        else:
            cursor.execute(f"UPDATE texts SET text = '{str(message.text)}' WHERE menu = 'Katalog'").fetchone()
            connection.commit()
            await bot.send_message(message.chat.id, "Изменен текст")

    except Exception as ex:
        await bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


@dp.message_handler(lambda msg: msg.text == "Нам доверяют")
async def get_doveryayut_admin(message):
    msg = await bot.send_message(message.from_user.id,
                                 'Отправь мне файл! Не более 200кб!\n'
                                 'Как сжать без фотошопа?\n'
                                 'Отправишь оригинал с сжатием в облако в своем телеграме и скачаешь его\n'
                                 'и отправишь мне сжатое изображение без сжатия! Только не ошибся '
                                 'жизнь бота в твоих руках! :)')
    bot.register_next_step_handler(msg, get_file_doveryayut_admin)


async def get_file_doveryayut_admin(message):
    try:
        if message.document:
            save_dir = 'media'
            file_name = message.document.file_name
            file_id_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)
            src = file_name

            with open(save_dir + "/" + src, 'wb') as new_file:
                new_file.write(downloaded_file)
            cursor.execute(f"UPDATE texts SET text = '{str(file_name)}' WHERE menu = 'Doveryayut'").fetchone()
            connection.commit()
            await bot.send_message(message.chat.id,
                                   "[*] File added:\nFile name - {}\nFile directory - {}".format(str(file_name),
                                                                                                 str(save_dir)))
        else:
            msg = await bot.send_message(message.chat.id, "Отправь мне без сжатия изображение")
            bot.register_next_step_handler(msg, get_file_doveryayut_admin)

    except Exception as ex:
        await bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


@dp.message_handler(lambda msg: msg.text == "Акции и бонусы")
async def get_aksiya_bonus_admin(message):
    msg = await bot.send_message(message.from_user.id, 'Отправь мне текст')
    bot.register_next_step_handler(msg, get_text_bonus_admin)


async def get_text_bonus_admin(message):
    try:
        text = message.text
        cursor.execute(f"UPDATE texts SET text = '{str(text)}' WHERE menu = 'Bonusi'").fetchone()
        connection.commit()
        await bot.send_message(message.chat.id, "Изменен текст")

    except Exception as ex:
        await bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


@dp.message_handler(lambda msg: msg.text == "Связаться с нами")
async def get_kontakt_admin(message):
    msg = await bot.send_message(message.from_user.id, 'Отправь мне текст')
    bot.register_next_step_handler(msg, get_text_kontakt_admin)


async def get_text_kontakt_admin(message):
    try:
        text = message.text
        cursor.execute(f"UPDATE texts SET text = '{str(text)}' WHERE menu = 'Kontakt'").fetchone()
        connection.commit()
        await bot.send_message(message.chat.id, "Изменен текст")

    except Exception as ex:
        await bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


@dp.message_handler(lambda msg: msg.text == "Преимущества")
async def get_preimushestva_admin(message):
    msg = await bot.send_message(message.from_user.id, 'Отправь мне текст')
    bot.register_next_step_handler(msg, get_text_preimushestva_admin)


async def get_text_preimushestva_admin(message):
    try:
        text = message.text
        cursor.execute(f"UPDATE texts SET text = '{str(text)}' WHERE menu = 'Preimushestva'").fetchone()
        connection.commit()
        await bot.send_message(message.chat.id, "Изменен текст")

    except Exception as ex:
        await bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


'''Пользовательский режим'''


@dp.message_handler(lambda msg: msg.text == "📂Скачать каталог")
async def get_catalogue(message):
    text = cursor.execute("SELECT text FROM texts WHERE menu = 'Katalog'").fetchone()
    x = text[0].rsplit("! ")
    if x[0] == 'file':
        doc = open(f'media/{x[1]}', 'rb')
        await bot.send_document(message.chat.id, doc)
    else:
        await bot.send_message(message.chat.id, text[0])


@dp.message_handler(lambda msg: msg.text == "📞Связаться с нами")
async def support(message):
    text = cursor.execute("SELECT text FROM texts WHERE menu = 'Kontakt'").fetchone()
    await bot.send_message(message.chat.id, text)


@dp.message_handler(lambda msg: msg.text == "🔸Акции и бонусы")
async def get_action_bonus(message):
    text = cursor.execute("SELECT text FROM texts WHERE menu = 'Bonusi'").fetchone()
    await bot.send_message(message.from_user.id, text[0])


@dp.message_handler(lambda msg: msg.text == "❔О Бизнес центре")
async def o_nas(message):
    markup = ReplyKeyboardMarkup()
    markup.add('🗺Инфраструктура')
    markup.add('✔Преимущества', '💳Оплата')
    markup.add('🚊Транспортная доступность')
    markup.add('🤝Нам доверяют')
    markup.add('🔙На главную')
    await bot.send_message(message.chat.id, "Мы рады, что вы интересуетесь нашим бизнес центром",
                           reply_markup=markup)


@dp.message_handler(lambda msg: msg.text == "🗺Инфраструктура")
async def get_infrastructure(message):
    msg = (
        '🏢  Бизнес центр «ARASH»- это современный деловой комплекс, '

        'отвечающий высоким стандартам бизнес-центра. Объект располагается в центре г.Ташкента '

        'в непосредственной близости городского сквера.\n\n'

        '📍 БЦ расположен по адресу: Мирабадский район, ул.Истикбол, дом 34\n\n'

        'Рядом с Бизнес Центром расположены:\n\n'

        '➖ ЖК Infinity\n\n'

        '➖ Кафе и рестораны: Efendi,  CoffeeMilk, Yapona Mama\n\n'

        '➖ Супермаркет Korzinka.uz')
    photo = open('media/infrastruktura.jpg', "rb")
    await bot.send_location(message.from_user.id, latitude=41.301801, longitude=69.288465)
    await bot.send_photo(message.from_user.id, photo, msg)
    photo.close()


@dp.message_handler(lambda msg: msg.text == "✔Преимущества")
async def get_infrastructure(message):  # noqa
    text_message = cursor.execute("SELECT text FROM texts WHERE menu = 'Preimushestva'").fetchone()

    await bot.send_message(message.from_user.id, text_message)


@dp.message_handler(lambda msg: msg.text == "🚊Транспортная доступность")
async def get_transport(message):
    msg = (
        '📍 Расположение в центре города создает удобство для посетителей и '
        'сотрудников, добираться до БЦ без личного транспортного средства.\n\n'
        '🚊 БЦ находится вблизи автобусной остановки, а также в 15 минутной '
        'доступности от трех станций метро: Ташкент, Сквер Амира Темура, Юнус Раджаби.')

    await bot.send_message(message.from_user.id, msg)


@dp.message_handler(lambda msg: msg.text == "💳Оплата")
async def get_price(message):
    msg = ('💳 Оплата производится 100% перечислением в сумах или валюте.\n\n'
           '🔘 Арендовав помещение Вы не будете думать:\n\n'
           '✔️ о ремонте\n\n'
           '✔️ о покупке мебели\n\n'
           '✔️ об оплате за коммунальные расходы (электроэнергия, теплоснабжение, водоснабжение)\n\n'
           '✔️ о парковочном месте\n\n'
           '✔️ об уборке\n\n'
           '✔️ об охране\n\n'
           '🔘 Все вышеуказанное уже включено в стоимость аренды.')
    await bot.send_message(message.from_user.id, msg)


@dp.message_handler(lambda msg: msg.text == "🤝Нам доверяют")
async def get_brands(message):
    text = cursor.execute("SELECT text FROM texts WHERE menu = 'Doveryayut'").fetchone()
    doc = open(f'media/{text[0]}', 'rb')
    await bot.send_photo(message.chat.id, doc)
    doc.close()


@dp.message_handler(lambda msg: msg.text == "🏢Планировки")
async def get_prices_command(msg: telebot.types.Message):
    """Получение всех планировок"""
    prices = get_planirovka()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for price in prices:
        keyboard.add(
            InlineKeyboardButton(
                text=price,
                callback_data=f'prc_{price}')
        )

    await bot.send_message(msg.from_user.id, 'Планировки:', reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('prc_'))
async def get_products_price_callback(callback_query: CallbackQuery):
    query = callback_query.data.replace('prc_', '')  # Убрать пометку callback'ов
    cursor.execute(f"Select pic1 From planirovka WHERE planirovka like '%{query}%'")
    photo_sql = cursor.fetchone()
    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                text=query,
                                reply_markup=None)
    await bot.send_document(callback_query.from_user.id, photo_sql[0], reply_markup='')


@dp.message_handler(lambda msg: msg.text == "🖼Галерея")
async def get_galereya(msg: telebot.types.Message):
    """Получение всех планировок"""
    prices = await get_galereyas()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for price in prices:
        keyboard.add(
            InlineKeyboardButton(
                text=price,
                callback_data=f'gal_{price}')
        )

    await bot.send_message(msg.from_user.id, 'Галерея:', reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('gal_'))
async def get_products_price_callback(callback_query: CallbackQuery):  # noqa
    query = callback_query.data.replace('gal_', '')  # Убрать пометку callback'ов
    cursor.execute(f"Select * From galereya WHERE galereya like '%{query}%'")
    rows_in = cursor.fetchall()
    photo_list = []
    for i in rows_in[0][2:]:
        if i is not None:
            photo_list.append(open(f'media/{i}', 'rb'))
    if photo_list:
        media = [InputMediaPhoto(i) for i in photo_list]
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=query,
                                    reply_markup=None)
        await bot.send_media_group(callback_query.from_user.id, media)
        list(map(lambda f: f.close(), photo_list))
    else:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=query,
                                    reply_markup=None)
        await bot.send_message(callback_query.from_user.id,
                               "Благодарим Вас за заинтересованность нашим бизнес центром!\n"
                               f"В скором времени здесь будут доступны фотографии раздела *{query}*",
                               parse_mode="Markdown")


user_dict = {}


class User:
    def __init__(self, client_id):
        self.client_id = client_id
        self.srok = None
        self.srok_temp = None
        self.nazvaniye = None
        self.username = None
        self.telegram_id = None


@dp.message_handler(lambda msg: msg.text == "👥Обслуживание клиентов")
async def send_welcome(message):
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    cursor.execute(f"Select * From clients WHERE telegram_id like '%{telegram_id}%'")
    user_data = cursor.fetchone()
    # print(user_data, "user_data")
    try:
        if not user_data:
            markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('🔙На главную')
            msg = await bot.send_message(message.chat.id,
                                         'Пожалуйста пройдите авторизацию, для этого отправьте '
                                         'ИНН номер фирмы в указанном формате:\n'
                                         '"*123456789*" - без кавычек', reply_markup=markup, parse_mode="Markdown")

            await bot.register_next_step_handler(msg, process_name_step)
        elif user_data[4] == telegram_id:
            markup = ReplyKeyboardMarkup()
            markup.add('Нужна срочная помощь?')
            markup.add('Оставить предложения и просьбы')
            markup.add('Пройти опрос')
            markup.add('🔚Выйти')
            markup.add('🔙На главную')
            await bot.send_message(message.chat.id, f"Добро пожаловать {first_name}!", reply_markup=markup)

    except Exception as e:
        await bot.reply_to(message, f'Ошибка в боте. Нажмите на /start \nКод ошибки: {e}')


async def process_name_step(message):
    try:
        chat_id_here = message.chat.id
        inn = message.text
        first_name = message.from_user.first_name
        if inn == u'🔙На главную':
            raise Exception('Отмена регистрации')

        elif not inn.isdigit():
            msg = await bot.reply_to(message, 'Отправьте нам только цифры!')
            await bot.register_next_step_handler(msg, process_name_step)
            return
        elif len(inn) != 9:
            msg = await bot.reply_to(message, 'Вы неправильно ввели ИНН. Он должен состоять из 9 цифр')
            await bot.register_next_step_handler(msg, process_name_step)
            return

        user = User(inn)  # Наследование класса User и присвоение к переменной user конструктора
        user_dict[chat_id_here] = user  # Добавление объекта класса User к глобальному словарю user_dict

        cursor.execute(f"Select * From clients WHERE inn like '%{inn}%'")
        rows_in = cursor.fetchall()
        if not rows_in:
            raise Exception("В базе нет такого номера договора")

        elif inn == rows_in[0][0]:
            user.client_id = rows_in[0][0]
            user.srok = rows_in[0][1]
            user.nazvaniye = rows_in[0][2]
            user.username = message.from_user.username
            user.telegram_id = chat_id_here
            sql = '''UPDATE clients
                        SET username = ?,
                        telegram_id = ? WHERE inn = ?'''
            cursor.execute(sql, (user.username, chat_id_here, user.client_id)).fetchone()
            connection.commit()
            markup = ReplyKeyboardMarkup()
            markup.add('Нужна срочная помощь?')
            markup.add('Оставить предложения и просьбы')
            markup.add('Пройти опрос')
            markup.add('🔚Выйти')
            markup.add('🔙На главную')
            await bot.send_message(message.chat.id,
                                   f"Добро пожаловать: _{first_name}!_ \nВаша фирма: *{rows_in[0][2]}*",
                                   parse_mode="Markdown", reply_markup=markup)
        else:
            raise Exception("Дата соглашения договора не совпадает")
    except Exception as e:
        if e.args == ('Дата соглашения договора не совпадает',):
            msg = await bot.send_message(message.chat.id, "Дата соглашения договора не совпадает")
            await bot.register_next_step_handler(msg, process_name_step)
        elif e.args == ('В базе нет такого номера договора',):
            msg = await bot.send_message(message.chat.id, "В базе нет такого номера договора!")
            await bot.register_next_step_handler(msg, process_name_step)
        elif e.args == ('Отмена регистрации',):
            await bot.send_message(message.chat.id, 'Вы отменили авторизацию.')
            await send_welcome_homepage(message)
        else:
            msg = await bot.send_message(message.chat.id, e.args)
            msg = await bot.send_message(message.chat.id, "Внутрення ошибка бота. Пожалуйста наберите /start")
            bot.register_next_step_handler(msg, process_name_step)


@dp.message_handler(lambda msg: msg.text == "🔚Выйти")
async def logout(message):
    sql = '''UPDATE clients
                            SET username = ?,
                            telegram_id = ? WHERE telegram_id = ?'''
    cursor.execute(sql, ('NULL', 'NULL', message.from_user.id)).fetchone()
    connection.commit()
    await bot.send_message(message.from_user.id, "Вы вышли из системы")
    send_welcome_homepage(message)


GROUP_ID = -598502968


@dp.message_handler(lambda msg: msg.text == "Оставить предложения и просьбы")
async def predlojeniye_first(message):
    msg = await bot.send_message(message.chat.id, "Введите Ваши предложения и просьбы")
    await bot.register_next_step_handler(msg, process_predlojeniye_step)


async def process_predlojeniye_step(message):
    try:
        text = message.text
        if text == u'Нужна срочная помощь?':
            raise Exception('Переход на помощь')
        elif text == u'Оставить предложения и просьбы' or text == u'Пройти опрос':
            msg = await bot.reply_to(message,
                                     'Пожалуйста, напишите предложение или нажмите на /cancel!')
            return await bot.register_next_step_handler(msg, process_predlojeniye_step)
        elif text == '/cancel':
            return await send_welcome(message)

        msg = message.chat.id
        telegram_id = message.from_user.id
        msg_id = message.message_id
        cursor.execute(f"Select * From clients WHERE telegram_id like '%{telegram_id}%'")
        user_data = cursor.fetchone()
        await bot.send_message(GROUP_ID, f"Новая просьба или предложение от фирмы: *{user_data[2]}*\n"
                                         f"👇👇👇👇👇👇👇👇👇", parse_mode="Markdown")
        await bot.forward_message(GROUP_ID, msg, msg_id)

        await bot.send_message(message.chat.id, "Ваше предложение и просьба отправлено на рассмотрение")
    except Exception as e:
        await pomosh_first(message)
        logging.error("Error while creating database connection: %s", e)


@dp.message_handler(lambda msg: msg.text == "Нужна срочная помощь?")
async def pomosh_first(message):
    msg = bot.send_message(message.chat.id, "Оставьте свою просьбу и мы рассмотрим в ближайшее время")
    await bot.register_next_step_handler(msg, process_pomosh_step)
    pass


async def process_pomosh_step(message):
    try:
        text = message.text
        if text == u'Оставить предложения и просьбы':
            raise Exception('Переход на предложения')
        elif text == u'Нужна срочная помощь?' or text == u'Пройти опрос':
            msg = await bot.reply_to(message,
                                     'Пожалуйста, напишите просьбу или нажмите на /cancel!')
            bot.register_next_step_handler(msg, process_predlojeniye_step)
            return
        elif text == '/cancel':
            return await send_welcome(message)
        msg = message.chat.id
        telegram_id = message.from_user.id
        msg_id = message.message_id
        cursor.execute(f"Select * From clients WHERE telegram_id like '%{telegram_id}%'")
        user_data = cursor.fetchone()
        await bot.send_message(GROUP_ID, f"Требуется помощь фирме: *{user_data[2]}*\n"
                                         f"👇👇👇👇👇👇👇👇👇", parse_mode="Markdown")
        await bot.forward_message(GROUP_ID, msg, msg_id)

        await bot.send_message(message.chat.id, "Ваша просьба на рассмотрении")
    except Exception as e:
        predlojeniye_first(message)
        logging.error("Error: {}".format(e))


@dp.message_handler(lambda msg: msg.text == "Пройти опрос")
async def oprosnik(message):
    link = cursor.execute("SELECT link FROM opros").fetchone()
    await bot.send_message(message.from_user.id,
                           f"Пожалуйста пройдите опрос по ссылке нажав на ссылку ниже:\n[ОПРОС ТУТ]({link[0]}) ",
                           disable_web_page_preview=True, parse_mode="MarkdownV2")


async def on_startup(dp):
    if not configs.DEBUG:
        await bot.set_webhook(configs.WEBHOOK_URL, drop_pending_updates=True)
    print("Bot started")
    print(await dp.bot.get_me())


async def on_shutdown(dp):
    print("Bot stopped")
    print("ETO DEBUG", configs.DEBUG)
    if not configs.DEBUG:
        await bot.delete_webhook()


if __name__ == '__main__':
    if configs.DEBUG:
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@")
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
    else:
        print("################################")
        start_webhook(
            dispatcher=dp,
            webhook_path=configs.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=configs.WEBAPP_HOST,
            port=configs.WEBAPP_PORT,
        )
