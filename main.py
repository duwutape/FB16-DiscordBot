import sqlite3

import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import datetime
import utils

### CONFIG
load_dotenv()
TOKEN = os.getenv('TOKEN')
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID'))

# grauer raum
GR_DEL_MIN = int(os.getenv('GR_DEL_MIN'))
GR_DEL_SEC = GR_DEL_MIN * 60

# client
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

### INIT DB
data = sqlite3.connect('data.db')
cursor = data.cursor()


### BOT EVENTS
@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    try:
        synced = await tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')


### message logging
@client.event
async def on_message_edit(before, after):
    if before.author == client.user:
        return

    log_channel = client.get_channel(int(os.getenv('LOG_CHANNEL_ID')))
    author = before.author
    channel = before.channel
    time_edit = after.edited_at.astimezone()

    msg_edit = discord.Embed()
    msg_edit.colour = discord.Colour.yellow()
    msg_edit.set_author(name=author, icon_url=f'{author.display_avatar}')
    msg_edit.description = f'**{before.jump_url} in <#{channel.id}> edited**'
    msg_edit.add_field(name='Before:', value=before.content, inline=False)
    msg_edit.add_field(name='After:', value=after.content, inline=False)
    msg_edit.set_footer(
        text=f'Author ID: {author.id} | Message ID: {before.id} | {time_edit.strftime('%d.%m.%Y %H:%M')}')
    await  log_channel.send(embed=msg_edit)


@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return

    log_channel = client.get_channel(int(os.getenv('LOG_CHANNEL_ID')))
    author = message.author
    channel = message.channel
    time_del = datetime.datetime.now().astimezone()

    msg_del = discord.Embed()
    msg_del.colour = discord.Colour.red()
    msg_del.set_author(name=author, icon_url=f'{author.display_avatar}')
    msg_del.description = f'**Message from {author.mention} deleted <#{channel.id}>**\n{message.content}'
    msg_del.set_footer(
        text=f'Author ID: {author.id} | Message ID: {message.id} | {time_del.strftime('%d.%m.%Y %H:%M')}')
    await log_channel.send(embed=msg_del)


### grauer raum
@tree.command(name='gr', description='Schickt Altklausuren vom ausgewählten Modul')
@app_commands.describe(modul='Abkürzung des Moduls')
async def gr(interaction, modul: str):
    cursor = utils.connect_db()
    modules_lower = utils.get_modules_lower(cursor)

    if modul.lower() in modules_lower:
        path = utils.get_path(cursor, modul.lower())
        try:
           sent = discord.Embed()
           sent.colour = discord.Colour.green()
           sent.title = f'Altklausren {utils.get_modul_name(cursor, modul.lower())}'
           sent.description = f'Bitte beachte, dass die Nachricht in {GR_DEL_MIN} Minuten gelöscht wird'
           await interaction.response.send_message(embed=sent, file=discord.File(fp=path), ephemeral=True,
                                                    delete_after=GR_DEL_SEC)
        except FileNotFoundError as e:
            no_file = discord.Embed()
            no_file.colour = discord.Colour.red()
            no_file.title = 'Keine Altklausuren zu dem Modul gefunden'
            no_file.description = f'Das ist nicht dein Fehler. Das Team wurde bereits benachrichtigt.'
            await interaction.response.send_message(embed=no_file, ephemeral=True, delete_after=GR_DEL_SEC)
            no_file_log = discord.Embed()
            no_file_log.colour = discord.Colour.red()
            no_file_log.title = f'Keine Altklausuren zu dem Modul {utils.get_modul_name(cursor, modul.lower())} gefunden'
            no_file_log.description = f'Unter dem Pfad `{path}` wurde keine Datei gefunden.'
            await client.get_channel(LOG_CHANNEL_ID).send(embed=no_file_log)

            MOD_IDS = utils.get_mod_ids()
            for mod_id in MOD_IDS:
                mod = client.get_user(int(mod_id))
                await mod.create_dm()
                await mod.dm_channel.send(embed=no_file_log)
    else:
        no_modul = discord.Embed()
        no_modul.colour = discord.Colour.red()
        no_modul.title = 'Keine Altklausur gefunden'
        no_modul.description = (f'Es wurde keine Altklausur für das angegebene Modul geunden.\n'
                                f'Eine Liste aller verfügbaren Module findest du in <#{int(os.getenv('GR_ANLEITUNG_CHANNEL_ID'))}>.\n'
                                f'Bitte überprüfe auch, ob du den Modulnamen richtig gescrieben hast.')
        await interaction.response.send_message(embed=no_modul, ephemeral=True, delete_after=GR_DEL_SEC)

    cursor.connection.close()


client.run(TOKEN)
