import discord
from discord import app_commands

import utils


def init(client, tree):
    @tree.command(name='latex', description='Gibt den angegeben Ausdruck als LaTeX-Ausdruck wieder')
    @app_commands.describe(ausdruck='Ausdruck, der in LaTeX angezeige werden soll')
    async def latex(interaction, ausdruck: str):
        result = utils.request_image(ausdruck)
        await interaction.response.send_message(file=discord.File(fp=result))

        utils.delete_file(result)
