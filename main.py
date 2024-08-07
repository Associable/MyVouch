import discord
from discord import app_commands
import os
import json

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

class AClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
            clear_console()
            await self.change_presence(status=discord.Status.dnd, activity=discord.Game("yes very good"))

# Command tree
intents = discord.Intents.default()
intents.message_content = True
client = AClient()
tree = app_commands.CommandTree(client)

# File to store vouches
VOUCHES_FILE = 'vouches.json'

# Function to load vouches from file
def load_vouches():
    if not os.path.exists(VOUCHES_FILE):
        return []
    with open(VOUCHES_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# Function to save vouches to file
def save_vouches(vouches):
    with open(VOUCHES_FILE, 'w') as f:
        json.dump(vouches, f, indent=4)

# Slash command for vouch
@tree.command(name='vouch', description='Vouch for your experience')
@app_commands.describe(
    message='Describe your experience',
    stars='Add an amount of stars for the vouch, from 1-5.',
    proof='Add an image/video as proof, it must be a png, jpg, jpeg, webp, gif or mp4 file.'
)
async def vouch(interaction: discord.Interaction, message: str, stars: int, proof: discord.Attachment = None):
    if stars < 1 or stars > 5:
        await interaction.response.send_message("Stars must be between 1 and 5.", ephemeral=True)
        return

    stars_emoji = '⭐' * stars
    proof_url = proof.url if proof else None

    # Create embed for vouch
    em = discord.Embed(title="New Vouch Created", color=discord.Color.dark_grey())
    em.add_field(name="Stars", value=stars_emoji, inline=False)
    em.add_field(name="Vouch", value=message, inline=False)
    em.add_field(name="Vouched by", value=f"<@{interaction.user.id}>", inline=True)
    em.add_field(name="Vouched at", value=interaction.created_at.isoformat(), inline=True)
    em.set_footer(text="devved by lunarings")
    em.timestamp = interaction.created_at

    if proof_url:
        em.add_field(name="Image/Video Proof", value=f"[Proof Link]({proof_url})", inline=False)

    # Save vouch to file
    vouches = load_vouches()
    vouch_number = len(vouches) + 1
    vouches.append({
        'user': interaction.user.id,
        'stars': stars_emoji,
        'experience': message,
        'proof': proof_url,
        'vouch_number': vouch_number,
        'timestamp': str(interaction.created_at)
    })
    save_vouches(vouches)

    await interaction.response.send_message(embed=em)

# Command to display all vouches
@tree.command(name='allvouches', description='Display all vouches')
async def allvouches(interaction: discord.Interaction):
    vouches = load_vouches()
    if not vouches:
        await interaction.response.send_message("No vouches available.", ephemeral=True)
        return

    for vouch in vouches:
        proof_text = f"[Proof Link]({vouch['proof']})" if vouch['proof'] else "No proof provided"
        stars_emoji = vouch['stars']
        em = discord.Embed(title="Vouch restored!", color=discord.Color.blue())
        em.add_field(name="Stars", value=stars_emoji, inline=False)
        em.add_field(name="Vouch", value=vouch['experience'], inline=False)
        em.add_field(name="Vouched by", value=f"<@{vouch['user']}>", inline=True)
        em.add_field(name="Vouched at", value=vouch['timestamp'], inline=True)
        em.add_field(name="Proof", value=proof_text, inline=False)
        em.set_footer(text="devved by lunarings")
        em.timestamp = interaction.created_at

        await interaction.channel.send(embed=em)

client.run('bot_tokenhere') #put ur bot token here
