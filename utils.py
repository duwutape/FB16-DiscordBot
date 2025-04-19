import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()


# grauer raum
def connect_db():
    db = sqlite3.connect(os.getenv('DB_PATH'))
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS altklausuren('
                   'modul TEXT PRIMARY KEY,'
                   'studiengang TEXT,'
                   'beschreibung TEXT'
                   'filepath TEXT'
                   ');')
    return cursor


def get_modules(cursor):
    modules_tuples = cursor.execute('SELECT modul FROM altklausren ORDER BY modul;').fetchall()
    modules = tuple_list_to_list(modules_tuples)
    return [modul.lower() for modul in modules]

def get_path(cursor, modul):
    path_tuple = cursor.execute(f'SELECT filepath FROM altklausren where modul = {modul};').fetchone()
    return tuple_to_str(path_tuple)

def tuple_list_to_list(tuple_list):
    return ['%s' % t for t in tuple_list]

def tuple_to_str(tuple):
    return ''.join(tuple)