import os
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

# grauer raum
def get_modules():
    #TODO get modules and return them as Literal
    modules = Literal['']
    return modules

def get_path(modul: str):
    GR_PATH = os.getenv('GR_PATH')
    GR_FILE = os.getenv('GR_FILE')

    return f'{GR_PATH}{modul}{GR_FILE}'