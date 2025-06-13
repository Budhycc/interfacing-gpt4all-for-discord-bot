import discord
from discord.ext import commands
import aiohttp
import time

API_URL = "http://localhost:4891/v1/chat/completions"
MODEL_NAME = "Lama 3 8B Instruct"

# Membaca token dari file token.txt
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Event: Bot siap
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} sudah online!')

# Command: !ping (command biasa)
@bot.command()
async def ping_bot(ctx):
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5,
        "temperature": 0.1
    }

    try:
        start = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                duration = int((time.time() - start) * 1000)
                if response.status == 200:
                    await ctx.send(f'✅ API aktif! Respon dalam {duration}ms.')
                else:
                    await ctx.send(f'⚠️ API error. Status: {response.status}')
    except Exception as e:
        await ctx.send(f'❌ Tidak bisa konek ke API.\n```{e}```')

# Command: !tanya (command biasa)
@bot.command()
async def tanya(ctx, *, pertanyaan: str = None):
    if pertanyaan is None:
        await ctx.send("❌ Kamu harus memberikan pertanyaan setelah perintah `!tanya`.")
        return

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": pertanyaan}],
        "max_tokens": 4000,
        "temperature": 0.28
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    jawaban = data['choices'][0]['message']['content']
                    MAX_LEN = 2000
                    for i in range(0, len(jawaban), MAX_LEN):
                        await ctx.send(jawaban[i:i+MAX_LEN])
                else:
                    await ctx.send(f'⚠️ Gagal ambil jawaban. Status: {response.status}')
    except Exception as e:
        await ctx.send(f'❌ Terjadi error:\n```{e}```')

# Slash Command: /ping
@bot.tree.command(name="ping", description="Cek koneksi ke API lokal")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.defer()
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5,
        "temperature": 0.1
    }

    try:
        start = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                duration = int((time.time() - start) * 1000)
                if response.status == 200:
                    await interaction.followup.send(f'✅ API aktif! Respon dalam {duration}ms.')
                else:
                    await interaction.followup.send(f'⚠️ API error. Status: {response.status}')
    except Exception as e:
        await interaction.followup.send(f'❌ Tidak bisa konek ke API.\n```{e}```')

# Slash Command: /tanya
@bot.tree.command(name="tanya", description="Kirim pertanyaan ke API lokal")
async def slash_tanya(interaction: discord.Interaction, pertanyaan: str):
    await interaction.response.defer()
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": pertanyaan}],
        "max_tokens": 4000,
        "temperature": 0.28
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    jawaban = data['choices'][0]['message']['content']
                    MAX_LEN = 2000
                    for i in range(0, len(jawaban), MAX_LEN):
                        await interaction.followup.send(jawaban[i:i+MAX_LEN])
                else:
                    await interaction.followup.send(f'⚠️ Gagal ambil jawaban. Status: {response.status}')
    except Exception as e:
        await interaction.followup.send(f'❌ Terjadi error:\n```{e}```')

# Sinkronisasi command tree (agar slash command muncul)
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'✅ Bot {bot.user} sudah online dan command tree sudah sinkron.')

# Jalankan bot
bot.run(TOKEN)
