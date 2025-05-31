import discord
from discord.ext import commands
from discord import option
import aiohttp
import time

API_URL = "http://localhost:4891/v1/chat/completions"
MODEL_NAME = "Lama 3 8B Instruct"
TOKEN = 'TOKEN BOT DISCORD PASTE HERE !!!!!!'

# Kombinasi antara commands.Bot dan discord.Bot
intents = discord.Intents.default()
intents.message_content = True

# Bot untuk command biasa
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot untuk slash command
slash_bot = discord.Bot(intents=intents)

# Event: Bot siap
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} sudah online!')

@slash_bot.event
async def on_ready():
    print(f'✅ Slash Bot {slash_bot.user} sudah online!')

# Command: !ping (untuk command biasa)
@bot.command()
async def ping_bot(ctx):
    """Cek koneksi ke API lokal dengan command biasa."""
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

# Command: !tanya (untuk command biasa)
@bot.command()
async def tanya(ctx, *, pertanyaan: str = None):
    """Kirim pertanyaan ke API dengan command biasa."""
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
@slash_bot.slash_command(name="ping", description="Cek koneksi ke API lokal")
async def ping(ctx: discord.ApplicationContext):
    await ctx.defer()
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
                    await ctx.respond(f'✅ API aktif! Respon dalam {duration}ms.')
                else:
                    await ctx.respond(f'⚠️ API error. Status: {response.status}')
    except Exception as e:
        await ctx.respond(f'❌ Tidak bisa konek ke API.\n```{e}```')

# Slash Command: /tanya
@slash_bot.slash_command(name="tanya", description="Kirim pertanyaan ke API lokal")
@option("pertanyaan", str, description="Apa yang ingin kamu tanyakan?")
async def tanya(ctx: discord.ApplicationContext, pertanyaan: str):
    await ctx.defer()
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
                        await ctx.send_followup(jawaban[i:i+MAX_LEN])
                else:
                    await ctx.respond(f'⚠️ Gagal ambil jawaban. Status: {response.status}')
    except Exception as e:
        await ctx.respond(f'❌ Terjadi error:\n```{e}```')

# Jalankan bot
bot.run(TOKEN)
slash_bot.run(TOKEN)
