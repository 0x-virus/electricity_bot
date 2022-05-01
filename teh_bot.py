import telebot
import json

token = ''
id = 780359440

bot = telebot.TeleBot(token)


######################################
def isAdmin(user_id):
    if user_id == id:
        return True
    return False
######################################


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.from_user.id,
        'Напишите сообщение, и через некоторое время на него ответит администратор')


@bot.message_handler(commands=['help'])
def _help(message):
    if isAdmin(message.from_user.id):
        text = '''/ans [id] [message] - ответить на вопрос
/list - список активных вопросов
/del [id] - 'тихое' удаление всех вопросов от пользователя
/send [id] [message] - отправить сообщение (если нет вопроса)
               '''
        bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['list'])
def _list(message):
    try:
        if isAdmin(message.from_user.id):
            file = open('json/messages.json', 'r')
            content = json.load(file)
            file.close()
            text = ''
            for i in content.keys():
                text += '\n' + i + ': ' + \
                    '\n                      '.join(content[i])

            if text:
                bot.send_message(id, text)
            else:
                bot.send_message(id, 'Нет активных вопросов')
    except Exception as Error:
        bot.send_message(id, 'Произошла ошибка ' + str(Error))


@bot.message_handler(commands=['ans'])
def _ans(message):
    try:
        if isAdmin(message.from_user.id):
            file = open('json/messages.json', 'r')
            content = json.load(file)
            file.close()
            text = message.text.split()
            if str(text[1]) in content.keys():
                bot.send_message(
                    int(text[1]), 'Ответ от администрации: ' + ' '.join(text[2:]))
                del content[text[1]]
                bot.send_message(id, 'Ответ отправлен')
                file = open('json/messages.json', 'w+')
                json.dump(content, file, ensure_ascii=False, indent=4)
            else:
                bot.send_message(
                    id, 'Вопроса от данного пользователя не сущестует')
    except Exception as Error:
        bot.send_message(id, 'Произошла ошибка ' + str(Error))


@bot.message_handler(commands=['del'])
def _del(message):
    try:
        if isAdmin(message.from_user.id):
            file = open('json/messages.json', 'r')
            content = json.load(file)
            file.close()
            text = message.text.split()
            if str(text[1]) in content.keys():
                del content[text[1]]
                bot.send_message(id, 'Вопрос удалён')
                file = open('json/messages.json', 'w+')
                json.dump(content, file, ensure_ascii=False, indent=4)
            else:
                bot.send_message(
                    id, 'Вопроса от данного пользователя не сущестует')
    except Exception as Error:
        bot.send_message(id, 'Произошла ошибка ' + str(Error))


@bot.message_handler(commands=['send'])
def _send(message):
    try:
        if isAdmin(message.from_user.id):
            text = message.text.split()
            bot.send_message(
                int(text[1]), 'Сообщение от администрации: ' + ' '.join(text[2:]))
            bot.send_message(id, 'Сообщение отправлено')
    except Exception as Error:
        bot.send_message(id, 'Произошла ошибка ' + str(Error))


@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        file = open('json/messages.json', 'r+')
        content = json.load(file)
        file.close()

        file = open('json/messages.json', 'w+')
        if str(message.from_user.id) in content.keys():
            content[str(message.from_user.id)] += [message.text]
        else:
            content[str(message.from_user.id)] = [message.text]
        json.dump(content, file, ensure_ascii=False, indent=4)
        file.close()
        bot.send_message(message.from_user.id, 'Вопрос отправлен')
        bot.send_message(id, 'Новый вопрос от пользователя ' +
                         str(message.from_user.id) + ': ' + message.text)
    except Exception as Error:
        bot.send_message(message.from_user.id,
                         'Произошла ошибка при отправке сообщения')
        bot.send_message(id, 'Произошла ошибка при отправке сообщения со стороны пользователя ' + message.from_user.id +
                         str(Error))


bot.polling()
