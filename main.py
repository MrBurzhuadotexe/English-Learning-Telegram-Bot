import telebot as tb
import random
import sched
import time


from time import sleep
from bot_class import Bot


bot = tb.TeleBot(Bot.get_token())


words = (('people', 'люди', 3),
         ('family', 'семья'),
         ('woman', 'женщина'),
         ('man', 'мужчина'),
         ('girl', 'девочка'),
         ('boy', 'мальчик'),
         ('child', 'ребёнок'),
         ('friend', 'друг'),
         ('husband', 'муж'),
         ('wife', 'жена'),
         ('name', 'имя'),
         ('head', 'голова'),
         ('face', 'лицо'),
         ('hand', 'рука'))


quastion_patterns = ('Переведи на английский слово ', '',
                     'Как будет ', ' на английском?',
                     'Как на английском будет ', '?',
                     'Как переводится ', '?',
                     'Слово ', ' переводиться как...',
                     'А ', '?',
                     '', '')
index = int()
plan = int()
completed_words = 0

def Reminder(message):
    bot.send_message(message.chat.id, 'Который час? Время учить английский!')


def Scheduler(message):
    global completed_words
    completed_words = 0

    scheduler = sched.scheduler(time.time, sleep)
    scheduler.enter(120, 1, Reminder, argument=(message,))
    scheduler.enter(120, 1, Scheduler, argument=(message,))
    scheduler.run()


# Function to send a random English word for a translation
def send_random_word(message):
    global index
    index = random.randint(0, 13)
    i = random.randint(0, 4) * 2
    bot.send_message(message.chat.id, quastion_patterns[i] +
                     f'<b>«{words[index][1]}»</b>'
                     + quastion_patterns[i+1], parse_mode='html')


def Mistaker(user_translation, actual_translation):
    shift = 0
    mistakes = 0
    for i in range(len(user_translation)):
        if i + shift >= len(actual_translation):
            break

        if user_translation[i] != actual_translation[i+shift]:
            if i + shift + 1 < len(actual_translation) and \
                    user_translation[i] == actual_translation[i+shift+1]:
                shift += 1
            mistakes += 1

    return mistakes + abs(len(user_translation) - len(actual_translation)) - shift


# Handler for start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, f"Привет, <b>{message.from_user.first_name}</b>. "
                                     f"Я Вики! Я помогу тебе выучить английский язык. Приступим?", parse_mode='html')

    markup = tb.types.InlineKeyboardMarkup()
    markup.add(tb.types.InlineKeyboardButton("10 слов в день", callback_data=10))
    markup.add(tb.types.InlineKeyboardButton("20 слов в день", callback_data=20))
    markup.add(tb.types.InlineKeyboardButton("35 слов в день", callback_data=35))
    markup.add(tb.types.InlineKeyboardButton("60 слов в день", callback_data=60))
    bot.send_message(message.chat.id, "Выбери подходящий план обучения:", reply_markup=markup)

    Scheduler(message)
    send_random_word(message)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global plan
    plan = callback.data



# Handler for providing information
@bot.message_handler(commands=['help', 'info'])
def handle_info(message):
    bot.send_message(message.chat.id, '')


# Handler for text messages
@bot.message_handler(func=lambda message: True,)
def handle_text(message):
    user_translation = message.text.strip().lower()
    actual_translation = words[index][0]

    user_mistakes = Mistaker(user_translation, actual_translation)
    allowed_mistakes = (len(actual_translation)-1)//4

    if user_mistakes > allowed_mistakes:
        bot.reply_to(message, "Неправильно :(")
        sleep(0.5)
        bot.send_message(message.chat.id, "Попробуй ещё разок")
        sleep(0.5)
        bot.send_message(message.chat.id, f"<b>{words[index][1]}</b>", parse_mode='html')
    else:
        if user_mistakes == 0:
            bot.reply_to(message, "Верно!")
        else:
            bot.reply_to(message, "Почти! Правильный ответ:"
                                  f" <b>{actual_translation}</b>", parse_mode='html')
        send_random_word(message)

        global completed_words, plan
        completed_words += 1
        if completed_words == plan:
            bot.send_message(message.chat.id, "Поздравляю! План на сегодня выполнен. Можно и отдохнуть :)")





if __name__ == "__main__":
    bot.polling()

