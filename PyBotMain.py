import telebot
import pyowm
import requests

#Переменная хранит токен Telegram
TOKEN = '939828420:AAGD9cCQJpQjE9I2t6Ugf0KI96QPJU6w-pA'

#LastCommand - словарь, хранит последние вызовы команд по ID_клиентов
LastCommand = {}

#UserInfo - словарь, хранит сведения регистрации пользователей
UserInfo = {}

#Lastlanguage - словарь, хранит сведения о языках перевода по ID_клиентов
Lastlanguage = {}

OpisaineHelp = """
                Список моих команд
                - /reg - зарегистрируй себя и я буду обращаться к тебе по имени
                - /weather          - я покажу тебе температуру в любом городе
                - /translation      - я переведу любой введенный текст
                - /language         - я расскажу тебе на какие языки я умею переводить
                - /help             - я расскажу тебе о том, что я умею
                """

Codelanguage = {'en': 'английский',
                'de': 'немецкий',
                'it': 'итальянский',
                'fr': 'французский',
                'ru': 'русский',
                'ja': 'японский',
                'zh': 'китайский'}

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['weather'])
def Command_One(message):
    """
    Обработка первой команды /weather- "Получение температуры воздуха в городе ..."
    Функция запрашивает у пользователя город, в котором он хочет узнать температуру
    :param message: сообщение
    """
    client_id = message.from_user.id
    NameClient = get_NameUsers(client_id)
    LastCommand[client_id] = 'Command_weather'
    bot.send_message(chat_id=client_id, text=f"{NameClient}Введи город, в котором хочешь узнать температуру: ")


@bot.message_handler(commands=['translation'])
def Command_Two(message):
    """
    Обработка второй команды /translation - "Перевод вводимого текста"
    Функция запрашивает у пользователя код языка перевода и переходит к функции get_language
    :param message: сообщение
    """
    client_id = message.from_user.id
    NameClient = get_NameUsers(client_id)
    LastCommand[client_id] = 'Command_translation'
    bot.send_message(chat_id=client_id, text=f"{NameClient} Введи код языка для перевода: ")
    bot.register_next_step_handler(message, get_language)


@bot.message_handler(commands=['help'])
def Command_help(message):
    """
    Обработка команды /help
    Функция выводит список команд, обрабатываемые ботом. Данные по скиспку команд хранятся в переменной OpisaineHelp
    :param message: сообщение
    """
    client_id = message.from_user.id
    LastCommand[client_id] = 'Command_Help'
    bot.send_message(chat_id=client_id, text=OpisaineHelp)


@bot.message_handler(commands=['reg'])
def Command_Reg(message):
    """
    Обработка команды /reg
    Функция последовательно запрашивает от пользователя ввести имя и на следующем шаге фамилию
    Регистрационные данные фиксируются в UserInfo
    :param message: сообщение
    """
    client_id = message.from_user.id
    LastCommand[client_id] = 'Command_Reg'
    UserInfo[client_id] = dict(name='', surnme='')
    bot.send_message(chat_id=client_id, text='Введи свое Имя:')
    bot.register_next_step_handler(message, get_name)


@bot.message_handler(commands=['language'])
def Command_language(message):
    """
    Обработка команды /language
    Функция выдает пользователю информацию в сообщении о языках и их кодах, на которые бот может переводить текст
    В качестве источника используется словарь Codelanguage
    :param message: сообщение
    """
    client_id = message.from_user.id
    OpisaineLang = 'Коды языков, на которые можно переводить текст\n'
    for key, value in Codelanguage.items():
        OpisaineLang = OpisaineLang + key + ' - ' + value + '\n'
    bot.send_message(chat_id=client_id, text=OpisaineLang)


def get_name(message):
    """
    Функция получает сообщение от пользователя с  его именем, фиксирует данные в словаре UserInfo
    и происходит запрос фамилии пользователя и переход к следующему шагу регистрации - получению и фиксированию фамилии
    :param message: сообщение
    """
    client_id = message.from_user.id
    UserInfo[client_id]['name'] = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    """
    Функция получает сообщение от пользователя с  его фамилией, фиксирует данные в словаре UserInfo
    :param message: сообщение
    """
    client_id = message.from_user.id
    UserInfo[client_id]['surnme'] = message.text
    bot.send_message(message.from_user.id, f" "\
            f"Очень приятно, {UserInfo[client_id]['name']} {UserInfo[client_id]['surnme']}"\
            "\nВыбери команду, которую ты хочешь выполнить, а для этого введи /help")
    del LastCommand[client_id]


def get_NameUsers(id_client):
    """
    Функция получает сведения о Фамилии и имени пользователя из UserInfo по его id для дальнейшего обращения
    к пользователю по ФИ
    :param id_client: идентификатор клиента
    :return:NameClient :type: String, Фамилия и имя пользователя
    """
    NameClient = ""
    if id_client in UserInfo:
        NameClient = f"{UserInfo[id_client]['name']} {UserInfo[id_client]['surnme']},"
    return NameClient


def get_owm(id_client, cityIn = 'Москва'):
    """
    Функция получает сведения и передает в качестве сообщения о текущей температуре воздуха в указанном городе
    :param id_client: идентификатор клиента
    :param cityIn: наименование города
    :return:TextTemperature :type: String, Строка с температурой воздуха в указанном городе
    """
    NameClient = get_NameUsers(id_client)

    owm = pyowm.OWM('37c9cd8d9a0ab92fe4fb0394c4cc4d76',language='ru')
    city = (cityIn)

    try:
        observation = owm.weather_at_place(city)
        w = observation.get_weather()
        temperature = w.get_temperature('celsius')
        TextTemperature = f"{NameClient}\nВ городе {cityIn} температура воздуха {temperature['temp']} °С"

    except Exception:

        TextTemperature = f"{NameClient}\n Не найден город '{cityIn}'"

    return TextTemperature


def translation(TextIn, Lang='en'):
    """
    Функция посредством Яндекс API переводит переданный в качестве парамета текст на указанный в параметре язык
    :param TextIn: текст для перевода
    :param Lang: кодировка языка, на который необходимо перевести текст
    :return: :type: String, Переведенный текст
    """
    URL = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    KEY_API = 'trnsl.1.1.20190811T111147Z.501264c49832e0cd.d798b3da3c82ce2a37d07402e1936eb1997dceec'
    param = {'key': KEY_API,
             'text': TextIn,
             'lang': Lang}
    try:

        req = requests.post(URL,data=param)
        d = eval(req.text)
        return d['text']

    except Exception:

        return 'Ошибка при выполнении запроса.'


def get_language(message):
    """
    Функция обрабатывает сообщение, в котором пользователь должен был ввести кодировку языка, на который необходимо
    перевести текст и переход на следующий этап - запрос текста для перевода
    :param message: Соообщение
    :return:
    """
    client_id = message.from_user.id
    NameClient = get_NameUsers(client_id)

    findlg = message.text.strip()

    if findlg in Codelanguage:
        printstr = f'{NameClient}\nЯ переведу текст на '
    else:
        findlg = 'en'
        printstr = f'{NameClient}\nЯ не могу перевести текст на указанный язык, поэтому я переведу на  '

    printstr = printstr + Codelanguage[findlg] + " язык\n"
    Lastlanguage[client_id] = findlg
    bot.send_message(message.from_user.id, printstr)
    bot.send_message(message.from_user.id, f'{NameClient}\nВведи текст для перевода:')
    bot.register_next_step_handler(message, get_translation)


def get_translation(message):
    """
    Функция обрабатывает сообщение пользователя, в котором содержится текст для перевода
    Переданный текст переводится функцией translation и в обратном сообщении возвращается переведенный текст
    :param message: Соообщение
    :return:
    """
    client_id = message.from_user.id
    TextTr = translation(message.text, Lastlanguage[client_id])
    bot.reply_to(message, text=TextTr)
    del LastCommand[client_id]


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """
    Функция по обработке текстовых сообщений, поступающих от пользователя
    :param message: Соообщение
    :return:
    """
    client_id = message.from_user.id

    # Если клиент зарегистрирован получим его Имя/Фамилию
    NameClient = get_NameUsers(client_id)

    # Обработка команды "Погода"
    if client_id in LastCommand and LastCommand[client_id] == 'Command_weather':
        bot.reply_to(message, text=get_owm(client_id, message.text))
        del LastCommand[client_id]

     # Обработка команды HELP
    elif client_id in LastCommand and LastCommand[client_id] == 'Command_Help':
        del LastCommand[client_id]

    # Обработка команды language
    elif client_id in LastCommand and LastCommand[client_id] == 'Command_language':
        del LastCommand[client_id]

    # Обработка команды регистрации
    elif client_id in LastCommand and LastCommand[client_id] == 'Command_Reg':
        bot.register_next_step_handler(message, get_name)

    elif "привет" in message.text.lower():

        bot.send_message(message.from_user.id, f"""Привет,{NameClient} введи команду /help и я расскажу, что я умею""")

    else:
        bot.send_message(message.from_user.id, f"{NameClient} Я не понимаю команду, которую ввели. Вызовите /help")


bot.polling(none_stop=True)
