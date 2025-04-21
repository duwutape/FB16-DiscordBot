import os
import shutil
import sqlite3
import requests
import discord
from dotenv import load_dotenv

import constants

load_dotenv()


# grauer raum
def connect_db():
    db = sqlite3.connect(os.getenv('DB_PATH'))
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS altklausuren('
                   'modul TEXT,'
                   'modul_lower TEXT,'
                   'studiengang TEXT,'
                   'beschreibung TEXT'
                   'filepath TEXT'
                   ');')
    return cursor


def close_db(cursor):
    cursor.connection.close()


def get_modules(cursor):
    modules_tuples = cursor.execute('SELECT modul FROM altklausuren ORDER BY modul;').fetchall()
    return tuple_list_to_list(modules_tuples)


def get_modules_lower(cursor):
    modules_tuples = cursor.execute('SELECT modul_lower FROM altklausuren ORDER BY modul_lower;').fetchall()
    modules = tuple_list_to_list(modules_tuples)
    return [modul.lower() for modul in modules]


def get_path(cursor, modul):
    path_tuple = cursor.execute(f"SELECT filepath FROM altklausuren WHERE modul_lower = '{modul}';").fetchone()
    return tuple_to_str(path_tuple)


def get_modul_name(cursor, modul):
    modul_name = cursor.execute(f"SELECT modul FROM altklausuren WHERE modul_lower = '{modul}';").fetchone()
    return tuple_to_str(modul_name)


def tuple_list_to_list(tuple_list):
    return ['%s' % t for t in tuple_list]


def tuple_to_str(tuple):
    return ''.join(tuple)


def get_mod_ids():
    mod_str = os.getenv('MOD_IDS')
    if len(mod_str) >= 1:
        return mod_str.split(',')
    else:
        return None


def create_available_modules(study):
    if study == 'inf':
        study_long = 'Informatik'
    elif study == 'etech':
        study_long = 'Elekrotechnik'
    else:
        study_long = 'Sonstiges'

    cursor = connect_db()
    modules = cursor.execute(
        f"SELECT modul, beschreibung FROM altklausuren WHERE studiengang = '{study}' ORDER BY modul").fetchall()

    embed = discord.Embed()
    embed.title = f'Altklausuren {study_long}'
    embed.add_field(name='Kürzel', value=create_embed_value(modules, 0))
    embed.add_field(name='Modul', value=create_embed_value(modules, 1))

    return embed


def create_embed_value(moduels, index: int):
    modules_formatted = ['%s' % modul[index] for modul in moduels]
    out = ''
    for modul in modules_formatted:
        out = out + f'{modul}\n'

    return out


# latex
def create_latex_code(ausdruck):
    return (r'\documentclass{article}'
            r'\usepackage{pagecolor}'
            r'\pagenumbering{gobble}'
            r'\begin{document}\pagecolor{white} $') + ausdruck + r'$ \end{document}'


def get_image_url(filename):
    return f'{constants.LATEX_SERVER_URL}/{filename}'


def get_image_path(filename):
    return f'{os.getenv('TEMP_FILE_PATH')}{filename}'


def request_image(ausdruck):
    payload = {
        'format': 'png',
        'code': create_latex_code(ausdruck),
        'density': 220,
        'quality': 100
    }
    req = requests.post(url=constants.LATEX_SERVER_URL, json=payload)
    if req.ok:
        jreq = req.json()
        if jreq['status'] == 'error':
            return
        filename = req.json()['filename']

        req_img = requests.get(url=get_image_url(filename), stream=True)
        if req_img.ok:
            with open(get_image_path(filename), 'wb') as out_file:
                shutil.copyfileobj(req_img.raw, out_file)

            return get_image_path(filename)


def delete_file(path):
    os.remove(path)
