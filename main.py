import datetime

import discord
from discord import app_commands
from dotenv import load_dotenv
import os

### CONFIG
load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


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


client.run(TOKEN)
