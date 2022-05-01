from bs4 import BeautifulSoup
import requests
import datetime
import telebot
import time
import json
from database import Database


def write_times(data):  # добавление информации в times.json
    file1 = open('json/times.json', 'w')
    json.dump(data, file1, ensure_ascii=False, indent=4)
    file1.close()


class Bot:
    def __init__(self):
        self.url = "https://www.mrsk-1.ru/ajax/disconn_list.php"
        self.token = ''
        self.json_directory = 'json/'
        self.end_obj = []

    def get(self):  # возвращение информации из сайта, info - post запрос
        next_week = datetime.timedelta(days=31) + datetime.datetime.today()
        day = str(datetime.datetime.today().day)
        month = str(datetime.datetime.today().month)
        year = str(datetime.datetime.today().year)
        next_day = str(next_week.day)
        next_month = str(next_week.month)
        next_year = str(next_week.year)

        obj = {  # post запрос
            "region": "36",
            "start": day + '.' + month + '.' + year,
            "end": next_day + '.' + next_month + '.' + next_year
        }

        resp = requests.post(self.url, data=obj)
        soup = BeautifulSoup(resp.text, 'html.parser')
        data = soup.select('tr')

        end_obj = []  # конечный список
        for j in range(0, len(data)):
            some_obj = {"region": data[j].find('td', {'class': 'region'}).text,
                        "district": data[j].find('td', {'class': 'district'}).text,
                        "location": data[j].find('td', {'class': 'location'}).text,
                        "object": data[j].find('td', {'class': 'object'}).text,
                        "disconn-start-date": data[j].find('td', {'class': 'disconn-start-date'}).text,
                        "disconn-start-time": data[j].find('td', {'class': 'disconn-start-time'}).text,
                        "disconn-end-date": data[j].find('td', {'class': 'disconn-end-date'}).text,
                        "disconn-end-time": data[j].find('td', {'class': 'disconn-end-time'}).text,
                        "branch": data[j].find('td', {'class': 'branch'}).text,
                        "res_title": data[j].find('td', {'class': 'res_title'}).text}
            end_obj.append(some_obj)
        self.end_obj = end_obj

    def send(self, name, channel, send_file):
        bot = telebot.TeleBot(self.token)
        news = self.end_obj  # обращение к сайту для получения данных

        print('Проверка.', datetime.datetime.now(), len(news))

        file = open(self.json_directory + 'times.json', 'r')
        try:  # пытаемся загрузить файл как json объект. если он пустой - вызов функции write_times()
            strings = json.load(file)
        except json.decoder.JSONDecodeError:
            write_times(news)
            strings = json.load(file)

        strings2 = []  # строки из times.json
        for x in strings:
            strings2.append(x)
        file.close()

        file = open(self.json_directory + 'times.json', 'w')
        mass = []

        try:  # пытаемся открыть файл, если он пустой - объявляем пустой список
            send = open(self.json_directory + send_file + '.json', 'r')
            send_strings = json.load(send)
            send.close()
        except json.decoder.JSONDecodeError:
            send_strings = []

        send = open(self.json_directory + send_file + '.json', 'w')  # открываем на запись
        send_mass = []

        for y in news:  # разбираем новые новости
            mass.append(y)  # сразу добавляем в основной массив
            if name in str(y).lower():
                if str(y) not in str(send_strings) and str(y) not in str(send_mass):  # если еще не отправлялся
                    # добавляем для записи в send.json и отправки
                    send_mass.append(y)
                    message = 'Регион: ' + y['region'].replace('\n', '') + '\n\n' + \
                              'Административный район: ' + y['district'].replace('\n', '') + '\n\n' + \
                              'Населенный пункт: ' + y['location'].replace('\n', '') + '\n\n' + \
                              'Улица: ' + y['object'].replace('\n', '') + '\n\n' + \
                              'Дата и время начала: ' + y['disconn-start-date'] + ' ' + y[
                                  'disconn-start-time'] + '\n\n' + \
                              'Дата и время окончания: ' + y['disconn-end-date'] + ' ' + y[
                                  'disconn-end-time'] + '\n\n' + \
                              'Филиал: ' + y['branch'].replace('\n', '') + '\n\n' + \
                              'РЭС: ' + y['res_title'].replace('\n', '')

                    try:  # если несколько сообщений, возможна ошибка. нужно подождить 60 секунд
                        bot.send_message(channel, message)
                        time.sleep(5)
                    except telebot.apihelper.ApiException:
                        time.sleep(60)
                        print('Исключение. Ждём 60 секунд')
                        bot.send_message(channel, message)
                    print(channel, message)

                    db = Database(send_file)  # запись в БД
                    db.add_row(y)

        print(len(send_mass))  # вывод сколько новых записей было отправлено

        send_mass += send_strings  # добавление новых записей к старым
        json.dump(send_mass, send, ensure_ascii=False, indent=4)  # запись в send.json
        json.dump(mass, file, ensure_ascii=False, indent=4)  # запись в times.json
        file.close()
        send.close()
