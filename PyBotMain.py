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

Codelanguage = {'en': 'английский','de': 'немецкий','it': 'итальянский','fr': 'французский', 'ru': 'русский', 'ja': 'японский', 'zh': 'китайский'}

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['weather'])
def Command_One(message):
    client_id = message.from_user.id
    NameClient = get_NameUsers(client_id)
    LastCommand[client_id] = 'Command_weather'
    bot.send_message(chat_id=client_id, text=f"{NameClient}Введите город, в котором хотите узнать температуру: ")

@bot.message_handler(commands=['translation'])
def Command_Two(message):
    client_id = message.from_user.id
    NameClient = get_NameUsers(client_id)
    LastCommand[client_id] = 'Command_translation'
    bot.send_message(chat_id=client_id, text=f"{NameClient} Введите код языка для перевода: ")
    bot.register_next_step_handler(message, get_language)

@bot.message_handler(commands=['help'])
def Command_help(message):
    client_id = message.from_user.id
    LastCommand[client_id] = 'Command_Help'

    bot.send_message(chat_id=client_id, text=OpisaineHelp)

@bot.message_handler(commands=['reg'])
def Command_Reg(message):
    client_id = message.from_user.id
    LastCommand[client_id] = 'Command_Reg'
    UserInfo[client_id] = dict(name='', surnme='')
    bot.send_message(chat_id=client_id, text='Введите Ваше Имя:')
    bot.register_next_step_handler(message, get_name)

@bot.message_handler(commands=['language'])
def Command_language(message):
    client_id = message.from_user.id
    OpisaineLang = 'Коды языков, на которые можно переводить текст\n'
    for key, value in Codelanguage.items():
        OpisaineLang = OpisaineLang + key + ' - ' + value + '\n'
    bot.send_message(chat_id=client_id, text=OpisaineLang)



def get_name(message): #получаем имя
    client_id = message.from_user.id
    UserInfo[client_id]['name'] = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message): #получаем фамилию
    client_id = message.from_user.id
    UserInfo[client_id]['surnme'] = message.text
    bot.send_message(message.from_user.id, f"""Очень приятно, {UserInfo[client_id]['name']} {UserInfo[client_id]['surnme']}
Выбери команду, которую ты хочешь выполнить, а для этого введи /help""")
    del LastCommand[client_id]

def get_NameUsers(id_client):
    NameClient = ""
    if id_client in UserInfo:
        NameClient = f"{UserInfo[id_client]['name']} {UserInfo[id_client]['surnme']},"
    return NameClient

def get_owm(id_client, cityIn = 'Москва'):
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
    bot.send_message(message.from_user.id, f'{NameClient}\nВведите текст для перевода:')
    bot.register_next_step_handler(message, get_translation)

def get_translation(message):
    client_id = message.from_user.id
    TextTr = translation(message.text, Lastlanguage[client_id])
    bot.reply_to(message, text=TextTr)
    del LastCommand[client_id]



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
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

    # Обработка команды HELP
    elif client_id in LastCommand and LastCommand[client_id] == 'Command_language':
        del LastCommand[client_id]

    # Обработка команды регистрации
    elif client_id in LastCommand and LastCommand[client_id] == 'Command_Reg':
        bot.register_next_step_handler(message, get_name)

    elif "привет" in message.text.lower():

        bot.send_message(message.from_user.id, f"""Привет,{NameClient} введи команду /help и я расскажу, что я умею""")

    else:
        bot.send_message(message.from_user.id, f"{NameClient} Напиши мне 'Привет' или вызови команду /help")


bot.polling(none_stop=True)
