import discord
from discord.ext import commands
from discord import option
import aiohttp
import time
import json

API_BASE = "http://localhost:1234"
MODELS_URL = f"{API_BASE}/api/v0/models"
CHAT_URL = f"{API_BASE}/v1/chat/completions"
COMP_URL = f"{API_BASE}/api/v0/completions"
EMBED_URL = f"{API_BASE}/api/v0/embeddings"

# Baca token bot dari token.txt
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(command_prefix="!", intents=intents)

async def http(session, method, url, **kwargs):
    async with session.request(method, url, **kwargs) as r:
        return r.status, await r.json()

# Event saat bot siap
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} sudah online!')

# ======== MODELS =========
@bot.command(description="List semua model yang tersedia")
async def models(ctx):
    async with aiohttp.ClientSession() as s:
        st, data = await http(s, "GET", MODELS_URL)
    if st == 200:
        lines = [f"- {m['id']} (state={m['state']}, max_ctx={m['max_context_length']})" for m in data["data"]]
        await ctx.respond("📦 Models:\n" + "\n".join(lines))
    else:
        await ctx.respond(f"❌ Error {st}")

@bot.command(description="Lihat info model tertentu")
@option("model", str, description="ID model")
async def modelinfo(ctx, model: str):
    async with aiohttp.ClientSession() as s:
        st, info = await http(s, "GET", f"{MODELS_URL}/{model}")
    if st == 200:
        await ctx.respond(f"Info `{model}`:\n```json\n{json.dumps(info, indent=2)}\n```")
    else:
        await ctx.respond(f"❌ Error {st}")

# ======== CHAT COMPLETION =========
@bot.command(description="Chat dengan LM Studio (fitur lengkap)")
@option("prompt", str, description="Apa pertanyaanmu?")
async def chat(ctx, prompt: str):
    await ctx.defer()
    payload = {
        "model": "your-model-id",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "stream": False,
        "ttl": 300,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_time",
                    "description": "Get current time",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "time_response",
                "schema": {
                    "type": "object",
                    "properties": {"time": {"type": "string"}},
                    "required": ["time"]
                }
            }
        }
    }
    async with aiohttp.ClientSession() as s:
        st, resp = await http(s, "POST", CHAT_URL, json=payload)
    if st == 200:
        msg = resp["choices"][0]["message"]
        if "tool_calls" in msg:
            now = time.strftime("%H:%M:%S")
            await ctx.send_followup(f"🛠 Memanggil fungsi `{msg['tool_calls'][0]['function']['name']}` → waktu: `{now}`")
        else:
            for i in range(0, len(msg["content"]), 2000):
                await ctx.send_followup(msg["content"][i:i+2000])
    else:
        await ctx.respond(f"❌ Status {st}")

# ======== TEXT COMPLETION =========
@bot.command(description="Gunakan endpoint completion biasa")
@option("prompt", str, description="Prompt teks biasa")
async def complete(ctx, prompt: str):
    await ctx.defer()
    payload = {
        "model": "your-model-id",
        "prompt": prompt,
        "max_tokens": 100
    }
    async with aiohttp.ClientSession() as s:
        st, resp = await http(s, "POST", COMP_URL, json=payload)
    if st == 200:
        await ctx.send_followup("📄 " + resp["choices"][0]["text"])
    else:
        await ctx.respond(f"❌ Status {st}")

# ======== EMBEDDINGS =========
@bot.command(description="Dapatkan embedding dari input")
@option("text", str, description="Teks untuk diembed")
async def embed(ctx, text: str):
    await ctx.defer()
    payload = {
        "model": "your-embed-model",
        "input": [text]
    }
    async with aiohttp.ClientSession() as s:
        st, resp = await http(s, "POST", EMBED_URL, json=payload)
    if st == 200:
        vec = resp["data"][0]["embedding"]
        await ctx.send_followup(f"🔗 Panjang: {len(vec)}\nAwal: {vec[:5]}…")
    else:
        await ctx.respond(f"❌ Status {st}")

# Jalankan bot
bot.run(TOKEN)