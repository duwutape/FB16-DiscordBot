import discord
from discord import app_commands
from dotenv import load_dotenv
import os

from modlues import latex, gr, botevents

load_dotenv()

def init():
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    botevents.init(client, tree)
    gr.init(client, tree)
    latex.init(client, tree)

    client.run(os.getenv('TOKEN'))
