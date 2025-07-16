import discord
from discord.ext import commands
from discord import option
import aiohttp
import time
import json
import re

API_BASE = "http://localhost:1234"
MODELS_URL = f"{API_BASE}/api/v0/models"
CHAT_URL = f"{API_BASE}/api/v0/chat/completions"
COMP_URL = f"{API_BASE}/api/v0/completions"
EMBED_URL = f"{API_BASE}/api/v0/embeddings"

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

model_id = "deepseek-r1-distill-llama-8b"

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(command_prefix="!", intents=intents)

MAX_CHUNK_SIZE = 1990  # agar total dengan pembungkus ``` <= 2000

def chunk_message(text, size=MAX_CHUNK_SIZE):
    return [text[i:i+size] for i in range(0, len(text), size)]

async def http(session, method, url, **kwargs):
    async with session.request(method, url, **kwargs) as r:
        return r.status, await r.json()

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} sudah online!')

# ===== MODELS =====
@bot.command(description="List semua model yang tersedia")
async def models(ctx):
    async with aiohttp.ClientSession() as s:
        st, data = await http(s, "GET", MODELS_URL)
    if st == 200:
        lines = [f"- {m['id']} (state={m['state']}, max_ctx={m['max_context_length']})" for m in data["data"]]
        text = "📦 Models:\n" + "\n".join(lines)
        chunks = chunk_message(text)
        await ctx.respond(f"```\n{chunks[0]}\n```")
        for chunk in chunks[1:]:
            await ctx.send_followup(f"```\n{chunk}\n```")
    else:
        await ctx.respond(f"❌ Status {st}")

@bot.command(description="Lihat info model tertentu")
@option("model", str, description="ID model")
async def modelinfo(ctx, model: str):
    async with aiohttp.ClientSession() as s:
        st, info = await http(s, "GET", f"{MODELS_URL}/{model}")
    if st == 200:
        info_json = json.dumps(info, indent=2)
        chunks = chunk_message(info_json)
        await ctx.respond(f"```json\n{chunks[0]}\n```")
        for chunk in chunks[1:]:
            await ctx.send_followup(f"```json\n{chunk}\n```")
    else:
        await ctx.respond(f"❌ Status {st}")

@bot.command(description="Pilih model yang akan digunakan")
@option("model", str, description="Model ID dari /models")
async def pilihmodel(ctx, model: str):
    global model_id
    model_id = model
    await ctx.respond(f"✅ Model aktif diset ke: `{model}`")

# ===== CHAT COMPLETION =====
@bot.command(description="Chat dengan LM Studio (fitur lengkap)")
@option("prompt", str, description="Apa pertanyaanmu?")
async def chat(ctx, prompt: str):
    await ctx.defer()
    if not model_id:
        await ctx.send_followup("❗ Model belum dipilih. Gunakan `/pilihmodel`")
        return

    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    async with aiohttp.ClientSession() as s:
        st, resp = await http(s, "POST", CHAT_URL, json=payload)
    
    if st == 200:
        content = resp["choices"][0]["message"]["content"].strip()
        # Hapus semua teks yang ada di antara <think> dan </think> (termasuk tag-nya)
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        chunks = chunk_message(content)
        for chunk in chunks:
            await ctx.send_followup(f"```\n{chunk}\n```")
    else:
        await ctx.respond(f"❌ Status {st}")


# ===== TEXT COMPLETION =====
@bot.command(description="Gunakan endpoint completion biasa")
@option("prompt", str, description="Prompt teks biasa")
async def complete(ctx, prompt: str):
    await ctx.defer()
    if not model_id:
        await ctx.send_followup("❗ Model belum dipilih. Gunakan `/pilihmodel`")
        return

    payload = {
        "model": model_id,
        "prompt": prompt,
        "max_tokens": 100
    }

    async with aiohttp.ClientSession() as s:
        st, resp = await http(s, "POST", COMP_URL, json=payload)

    if st == 200:
        text = resp["choices"][0]["text"].strip()
        chunks = chunk_message(text)
        for chunk in chunks:
            await ctx.send_followup(f"```\n{chunk}\n```")
    else:
        await ctx.respond(f"❌ Status {st}")

# ===== EMBEDDINGS =====
@bot.command(description="Dapatkan embedding dari input")
@option("text", str, description="Teks untuk diembed")
async def embed(ctx, text: str):
    await ctx.defer()
    if not model_id:
        await ctx.send_followup("❗ Model belum dipilih. Gunakan `/pilihmodel`")
        return

    payload = {
        "model": model_id,
        "input": [text]
    }

    async with aiohttp.ClientSession() as s:
        st, resp = await http(s, "POST", EMBED_URL, json=payload)

    if st == 200:
        vec = resp["data"][0]["embedding"]
        embed_info = f"🔗 Panjang embedding: {len(vec)}\nAwal vector: {vec[:5]}…"
        chunks = chunk_message(embed_info)
        for chunk in chunks:
            await ctx.send_followup(f"```\n{chunk}\n```")
    else:
        await ctx.respond(f"❌ Status {st}")

bot.run(TOKEN)
