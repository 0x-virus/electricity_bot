import os
import sqlite3


class Database:
    def __init__(self, filename):
        self.filename = filename
        self.database_directory = 'database/'
        if not os.path.exists(self.database_directory + self.filename + '.db'):
            self.create_database()
        self.connection = sqlite3.connect(self.database_directory + self.filename + '.db')
        self.cursor = self.connection.cursor()

    def create_database(self):  # создание БД
        self.cursor = sqlite3.connect(self.database_directory + self.filename + '.db')
        self.cursor.execute('''CREATE TABLE ''' + self.filename + ''' (id INTEGER PRIMARY KEY, region TEXT, 
        district TEXT, location TEXT, object TEXT, disconn_start_date TEXT, disconn_start_time TEXT, 
        disconn_end_date TEXT, disconn_end_time TEXT, branch TEXT, res_title TEXT);''')

    def add_row(self, row):  # запись новой строки в БД
        mass = [row['region'], row['district'], row['location'], row['object'], row['disconn-start-date'],
                row['disconn-start-time'], row['disconn-end-date'], row['disconn-end-time'], row['branch'],
                row['res_title']]
        query = '''INSERT INTO ''' + self.filename + ''' (region, district, location, object, disconn_start_date,
         disconn_start_time, disconn_end_date, disconn_end_time, branch, res_title) VALUES \
         (\'''' + ('\',\''.join(mass)).replace('\n', '') + '''\');'''
        print(query)
        self.cursor.execute(query)
        self.connection.commit()
