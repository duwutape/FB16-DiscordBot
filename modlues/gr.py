import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import constants
import utils

load_dotenv()

def init(client, tree):


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
                sent.description = f'Bitte beachte, dass die Nachricht in {os.getenv('GR_DEL_MIN')} Minuten gelöscht wird'
                await interaction.response.send_message(embed=sent, file=discord.File(fp=path), ephemeral=True,
                                                        delete_after=constants.GR_DEL_SEC)
            except FileNotFoundError as e:
                no_file = discord.Embed()
                no_file.colour = discord.Colour.red()
                no_file.title = 'Keine Altklausuren zu dem Modul gefunden'
                no_file.description = f'Das ist nicht dein Fehler. Das Team wurde bereits benachrichtigt.'
                await interaction.response.send_message(embed=no_file, ephemeral=True, delete_after=constants.GR_DEL_SEC)
                no_file_log = discord.Embed()
                no_file_log.colour = discord.Colour.red()
                no_file_log.title = f'Keine Altklausuren zu dem Modul {utils.get_modul_name(cursor, modul.lower())} gefunden'
                no_file_log.description = f'Unter dem Pfad `{path}` wurde keine Datei gefunden.'
                await client.get_channel(int(os.getenv('LOG_CHANNEL_ID'))).send(embed=no_file_log)

                MOD_IDS = utils.get_mod_ids()
                if MOD_IDS is not None:
                    for mod_id in MOD_IDS:
                        mod = client.get_user(int(mod_id))
                        await mod.create_dm()
                        await mod.dm_channel.send(embed=no_file_log)
        else:
            no_modul = discord.Embed()
            no_modul.colour = discord.Colour.red()
            no_modul.title = 'Keine Altklausur gefunden'
            no_modul.description = (f'Es wurde keine Altklausur für das angegebene Modul geunden.\n'
                                    f'Eine Liste aller verfügbaren Module findest du in <#{os.getenv('GR_ANLEITUNG_CHANNEL_ID')}>.\n'
                                    f'Bitte überprüfe auch, ob du den Modulnamen richtig gescrieben hast.')
            await interaction.response.send_message(embed=no_modul, ephemeral=True, delete_after=constants.GR_DEL_SEC)

        utils.close_db(cursor)


    @tree.command(name='anleitung', description='Schickt die Anleitung für den Grauen Raum in den Anleitungschannel')
    async def anleitung(interaction):
        anleitung_channel = client.get_channel(int(os.getenv('GR_ANLEITUNG_CHANNEL_ID')))
        await anleitung_channel.send('# Wichtige Infos zum Grauen Raum\n'
                                     '## Wie benutze ich den Bot?\n'
                                     'Mit dem Befehl `/gr [modul]` bekommst du die zu dem Modul vorhanden Alklausuren.\n'
                                     f'Die Anfrage muss in <#{os.getenv('GR_ANFRAGEN_CHANNEL_ID')}> gestellt werden.\n'
                                     'Die Kürzel der Module sind dabei nicht case-sensitive. Alle verfügbaren Module findes du weiter unten im Channel.\n'
                                     '\n'
                                     '## Achtung:\n'
                                     f'Die Dateien sind nur für die Person sichtbar, die sie angefragt hat und löschen sich selbst nach {os.getenv('GR_DEL_MIN')}.\n'
                                     '**Weitervereitung der Dateien ist strengstens verboten.**\n'
                                     '\n'
                                     '## Warum veröffentlichen wir die Altklausuren nicht einfach?\n'
                                     'Natürlich könnten wir die Altklausuren auf GoogleDrive oder Moodle per Download zur Verfügung stellen.\n'
                                     'Die Altklausuren sind jedoch Urheberrechtlich geschützt und sind Werke der jeweiligen Professoren/Dozenten.\n'
                                     '\n'
                                     '## Was ist, wenn ich eine Altklausur haben will, die nicht auf der Liste steht?\n'
                                     'Wenn ein Modul nicht auf der List steht, dann gibt es schlicht keine Altklausur dazu. Wir bemühen uns aber die Liste stetig zu erweitern.\n'
                                     '\n'
                                     '## Ihr habt Altklausuren, die noch nicht auf unserem Discord-Server zur Verfügung stehen?\n'
                                     'Schreibt uns an `grauerraum-fsr16@uni-kassel.de` und wir schauen, ob und wie wir sie hier veröffentlichen können.\n'
                                     '\n'
                                     '## Ihr möchtet Altklausuren ausdrucken?\n'
                                     f'Gegen einen geringen Beitrag könnt ihr das bei uns in der Fachschaft machen. Während der Vorlesungszeit könnt ihr {os.getenv('GR_ZEITEN')} '
                                     f'vorbeikommen oder schreibt an `grauerraum-fsr16@uni-kassel.de`, um einen Termin zu vereinbaren. Eine Terminvereinbarung ist auch außerhalb der Vorlesungszeit möglich.')

        await interaction.response.send_message('Anleitung gesendet')


    @tree.command(name='module', description='Sendet alle verfügbaren Module in den Anleitungschannel')
    async def module(interaction):
        inf = utils.create_available_modules('inf')
        etech = utils.create_available_modules('etech')
        sonst = utils.create_available_modules('sonst')

        anleitung_channel = client.get_channel(int(os.getenv('GR_ANLEITUNG_CHANNEL_ID')))
        await anleitung_channel.send(embed=inf)
        await anleitung_channel.send(embed=etech)
        await anleitung_channel.send(embed=sonst)

        await interaction.response.send_message('Verfügbare Module gesendet')
