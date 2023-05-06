import base64
import os.path
import sqlite3

import telebot
from telebot import types
from random import uniform
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

# Константы для хранения информации о квесте
QUESTIONS = {
    1: {'question': 'Как его зовут?','options': ['Саске!', 'Наруто', 'Орочимару'], 'answer': 'Наруто'},
    2: {'question': 'Какое ниндзюцу освоил Наруто в начале первого сезона?','options': ['Теневое Клонирование', 'Аматерасу', 'Расенган'], 'answer': 'Теневое Клонирование'},
    3: {'question': 'Как звали родителей Наруто?','options': ['Фугаку и Микото', 'Джирайа и Цунаде', 'Минато и Кушина'], 'answer': 'Минато и Кушина'},
    4: {'question': 'Под каким номером была команда Асумы,состоящая из Конохомары Нара,Чоуджи Акимичи, Ино Яманаки?','options': ['10', '7', '2'], 'answer': '10'},
    5: {'question': 'Джинчуурики какого хвостатого был Гаара?', 'options': ['Шукаку', 'Исобу', 'Шинжу'], 'answer': 'Шукаку'},
    6: {'question': 'Что означает кандзи на левой стороне лба у Гаары?','options': ['Сила', 'Любовь', 'Смерть'], 'answer': 'Любовь'},
    7: {'question': 'Сколько шаринганов было у Данзо Шимуры?','options': ['11', '10', '9'], 'answer': '11'},
    8: {'question': 'Какой клан использовал специальных жуков в бою?','options': ['Хьюга', 'Нара', 'Абураме'], 'answer': 'Абураме'},
    9: {'question': 'Три великих доудзюцу', 'options': ['Шаринган,бьякуган,риннеган', 'Шаринган,бьякуган,джоган', 'Кецьюриган,шаринган,бьякуган'], 'answer': 'Шаринган,бьякуган,риннеган'},
    10: {'question': 'Сколько человек было в Мечниках Тумана', 'options': ['5', '10', '7'], 'answer': '7'},
    11: {'question': 'Какую деревню основал Орочимару?','options': ['Скрытого звука', 'Скрытого клыка', 'Скрытого ключ'], 'answer': 'Скрытого звука'},
    12: {'question': 'Как назывался меч,которым когда-то обладал Джузо Бива?', 'options': ['Разрушитель', 'Разделитель', 'Обезглавлеватель'], 'answer': 'Обезглавлеватель'},
    13: {'question': 'Какому богу покланялся Хидан','options': ['Джашин', 'Кагуя', 'Ишшики'], 'answer': 'Джашин'},
    14: {'question': 'Кто дал Джирайе, Цунаде и Орочимару звание великих саннинов листа?','options': ['Ханзо Саламандра', 'Шиноби скрытого камня', 'Хирузен Сарутоби'], 'answer': 'Ханзо Саламандра'},
    15: {'question': 'Кто является самым младшим в клане Акацуки','options': ['Итачи', 'Дейдара', 'Сасори'], 'answer': 'Дейдара'},
}

current_level = 1
scores = 0

db_data_path = "db_data"
os.mkdir("db_data")

@bot.message_handler(commands=['start'])
def start(message):
    global current_level, scores
    current_level = 1
    scores = 0
    bot.send_message(message.chat.id, f'Приветствую тебя,сяо, {message.from_user.first_name}! Ты попал в этот удивительный квест. Надеюсь тебе удастся его пройти! Начнём с низов. Первый вопрос: {QUESTIONS[1]["question"]}')
    send_question(message)

def send_question(message):
    try:
        connecter = sqlite3.connect("bdForBot.db")
        img = connecter.execute('SELECT imgPath FROM images WHERE id = ?',(current_level,)).fetchone()

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for option in QUESTIONS[current_level]['options']:
            markup.add(types.KeyboardButton(option))

        photo_path = os.path.join(db_data_path,str(current_level) +".jpg")

        with open(photo_path,"wb") as fh:
            fh.write(sqlite3.Binary(img[0]))
            bot.send_photo(message.chat.id, open(photo_path,"rb"))
        bot.send_message(message.chat.id, QUESTIONS[current_level]['question'], reply_markup=markup)

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite",error)
    finally:
        if connecter:
            connecter.close()
            print("Соединение закрыто")

@bot.message_handler(content_types=['text'])
def check_answer(message):
    global current_level, scores
    if current_level == 15:  # Если это 15-й вопрос
        if uniform(0, 1) < 1 / 2:  # Генерируем случайное число от 0 до 1 и проверяем, меньше ли оно 1/2
            is_correct = True
        else:
            is_correct = False
    else:
        is_correct = message.text.lower() == QUESTIONS[current_level]['answer'].lower()

    if is_correct:
        scores += 1
        if current_level < 15:
            current_level += 1
            bot.send_message(message.chat.id, f'Браво! Переходим к следующему вопросу:')
            send_question(message)
        else:
            bot.send_message(message.chat.id, f'Вам удалось набрать {scores} баллов!')
    else:
        scores -= 1
        bot.send_message(message.chat.id, 'К сожалению,это неправильный ответ. Подумайте лучше.')
        send_question(message)

bot.polling()