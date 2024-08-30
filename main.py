import os
import json
import discord
from discord import app_commands
from discord.ext import commands

# Constants
VOUCHES_FILE = 'vouches.json'
BOT_TOKEN = 'bot_tokenhere'  # Replace with your actual bot token

# Utility functions
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def load_vouches():
    if not os.path.exists(VOUCHES_FILE):
        return []
    with open(VOUCHES_FILE, 'r') as f:
        return json.load(f)

def save_vouches(vouches):
    with open(VOUCHES_FILE, 'w') as f:
        json.dump(vouches, f, indent=4)

# Bot setup
class VouchBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Command tree synced.")

    async def on_ready(self):
        await self.change_presence(status=discord.Status.dnd, activity=discord.Game("Vouching"))
        print(f'{self.user} has connected to Discord!')
        clear_console()

bot = VouchBot()

# Command functions
@bot.tree.command(name='vouch', description='Vouch for your experience')
@app_commands.describe(
    message='Describe your experience',
    stars='Add an amount of stars for the vouch, from 1-5.',
    proof='Add an image/video as proof, it must be a png, jpg, jpeg, webp, gif or mp4 file.'
)
async def vouch(interaction: discord.Interaction, message: str, stars: int, proof: discord.Attachment = None):
    if not 1 <= stars <= 5:
        await interaction.response.send_message("Stars must be between 1 and 5.", ephemeral=True)
        return

    stars_emoji = '⭐' * stars
    proof_url = proof.url if proof else None

    em = discord.Embed(title="New Vouch Created", color=discord.Color.dark_grey())
    em.add_field(name="Stars", value=stars_emoji, inline=False)
    em.add_field(name="Vouch", value=message, inline=False)
    em.add_field(name="Vouched by", value=f"<@{interaction.user.id}>", inline=True)
    em.add_field(name="Vouched at", value=interaction.created_at.isoformat(), inline=True)
    if proof_url:
        em.add_field(name="Image/Video Proof", value=f"[Proof Link]({proof_url})", inline=False)
    em.set_footer(text="devved by lunarings")
    em.timestamp = interaction.created_at

    vouches = load_vouches()
    vouches.append({
        'user': interaction.user.id,
        'stars': stars_emoji,
        'experience': message,
        'proof': proof_url,
        'vouch_number': len(vouches) + 1,
        'timestamp': str(interaction.created_at)
    })
    save_vouches(vouches)

    await interaction.response.send_message(embed=em)

@bot.tree.command(name='allvouches', description='Display all vouches')
async def allvouches(interaction: discord.Interaction):
    vouches = load_vouches()
    if not vouches:
        await interaction.response.send_message("No vouches available.", ephemeral=True)
        return

    for vouch in vouches:
        proof_text = f"[Proof Link]({vouch['proof']})" if vouch['proof'] else "No proof provided"
        em = discord.Embed(title="Vouch restored!", color=discord.Color.blue())
        em.add_field(name="Stars", value=vouch['stars'], inline=False)
        em.add_field(name="Vouch", value=vouch['experience'], inline=False)
        em.add_field(name="Vouched by", value=f"<@{vouch['user']}>", inline=True)
        em.add_field(name="Vouched at", value=vouch['timestamp'], inline=True)
        em.add_field(name="Proof", value=proof_text, inline=False)
        em.set_footer(text="devved by lunarings")
        em.timestamp = interaction.created_at

        await interaction.channel.send(embed=em)

# Run the bot
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
