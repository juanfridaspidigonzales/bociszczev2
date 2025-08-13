import discord
from discord.ext import commands
from db import init_db, get_character, create_or_update_character, get_spell_training_counts
from query import run_query
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

class Przycisk(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(label="Czar", style=discord.ButtonStyle.primary, custom_id="Czar")
    async def czarmuchy(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("spueradaj", ephemeral=True)
            return
        await interaction.response.send_message("muchy", ephemeral=False)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend slash")
    except Exception as e:
        print(f"Błąd synchronizacji {e}")


@bot.tree.command(name="profil", description="Wyświetla profil twojej postaci.")
async def profil(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    try:
        char = get_character(user_id)
        spell_counts = get_spell_training_counts(user_id)
    except Exception as e:
        await interaction.response.send_message(
            f"Wystąpił błąd podczas odczytu profilu: {e}",
            ephemeral=True
        )
        return
    if not char:
        await interaction.response.send_message(
            "Nie masz jeszcze postaci. Użyj komendy `/stworzpostac` aby ją utworzyć.",
            ephemeral=True
        )
        return

    if spell_counts:
        lines = []
        for spell, count in spell_counts:
            if count == 1:
                suf = "trening"
            elif 2 <= count <= 4:
                suf = "treningi"
            else:
                suf = "treningów"
            lines.append(f"- **{spell}** — {count} {suf}")
        spells_text = "\n".join(lines)
    else:
        spells_text = "Brak nauczonych zaklęć."

    embed = discord.Embed(
        title="Profil postaci",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
    )
    embed.add_field(name="Imię postaci", value=char['name'], inline=False)
    embed.add_field(name="Opis umiejętności", value=char['description'], inline=False)
    embed.add_field(name="Zaklęcia i treningi", value=spells_text, inline=False)
    embed.set_footer(text=f"ID użytkownika: {interaction.user.id}")

    view = Przycisk(interaction.user)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(
    name="stworzpostac",
    description="Tworzy lub aktualizuje profil postaci — podaj imię i krótki opis umiejętności."
)
async def create_postac(
    interaction: discord.Interaction,
    nazwa_postaci: str,
    opis_umiejetnosci: str
):
    user_id = str(interaction.user.id)
    char_exists = bool(get_character(user_id))
    create_or_update_character(user_id, nazwa_postaci, opis_umiejetnosci)

    message = (
        f"Postać **{nazwa_postaci}** została zaktualizowana."
        if char_exists else
        f"Postać **{nazwa_postaci}** została stworzona."
    )

    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="trening", description="Generuje opis treningu zaklęcia.")
async def trening(
    interaction: discord.Interaction,
    zaklęcie: str,
    kontekst: str
):
    user_id = str(interaction.user.id)
    char = get_character(user_id)

    if not char:
        await interaction.response.send_message(
            "Musisz najpierw stworzyć postać komendą `/stworzpostac`.",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    chunks = await run_query(genai_model, zaklęcie, kontekst, char, user_id)

    if isinstance(chunks, str):
        await interaction.followup.send(content=f"Błąd: {chunks}")
        return

    await interaction.followup.send(
        content=f"Wynik treningu zaklęcia **{zaklęcie}** dla {char['name']}:"
    )

    for chunk in chunks:
        await interaction.followup.send(chunk)
        await asyncio.sleep(1.5)


def run_bot():
    global genai_model
    init_db()

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not TOKEN:
        print("Brak tokena bota w DISCORD_BOT_TOKEN")
        return
    if not GEMINI_API_KEY:
        print("Brak klucza API w GEMINI_API_KEY")
        return

    # Konfiguracja Gemini API
    genai.configure(api_key=GEMINI_API_KEY)
    genai_model = genai.GenerativeModel('gemini-2.0-flash-lite') # Używam Flasha ze względu na szybkość odpowiedzi

    bot.run(TOKEN)
