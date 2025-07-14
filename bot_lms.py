import discord, aiohttp, time, json
from discord.ext import commands
from discord import option

API_BASE = "http://localhost:1234"
# API_URLs
MODELS_URL = f"{API_BASE}/api/v0/models"
CHAT_URL = f"{API_BASE}/v1/chat/completions"
COMP_URL = f"{API_BASE}/api/v0/completions"
EMBED_URL = f"{API_BASE}/api/v0/embeddings"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
slash = discord.Bot(intents=intents)

async def http(session, method, url, **kwargs):
    async with session.request(method, url, **kwargs) as r:
        return r.status, await r.json()

@bot.command()
async def models(ctx):
    """List all models."""
    async with aiohttp.ClientSession() as s:
        st, data = await http(s, "GET", MODELS_URL)
    if st==200:
        lines = [f"- {m['id']} (state={m['state']}, max_ctx={m['max_context_length']})" for m in data["data"]]
        await ctx.send("📦 Models:\n" + "\n".join(lines))
    else:
        await ctx.send(f"❌ Error {st}")

@bot.command()
async def modelinfo(ctx, model: str):
    """Get info about a specific model."""
    async with aiohttp.ClientSession() as s:
        st, info = await http(s, "GET", f"{MODELS_URL}/{model}")
    if st==200:
        await ctx.send(f"Info `{model}`:\n" + json.dumps(info, indent=2))
    else:
        await ctx.send(f"❌ Error {st}")

@bot.command()
async def chat(ctx, *, prompt: str):
    """Chat completion with tools, TTL, structured output."""
    async with aiohttp.ClientSession() as s:
        payload = {
            "model": "your-model-id",
            "messages": [{"role":"user","content":prompt}],
            "temperature":0.5,
            "stream": False,
            "ttl": 300,
            "tools": [
                {
                  "type": "function",
                  "function": {
                    "name": "get_time",
                    "description": "Get current time",
                    "parameters": {"type":"object","properties":{}}
                  }
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name":"time_response",
                    "schema":{
                        "type":"object",
                        "properties":{"time":{"type":"string"}},
                        "required":["time"]
                    }
                }
            }
        }
        st, resp = await http(s, "POST", CHAT_URL, json=payload)
    if st==200:
        if resp["choices"][0]["message"].get("tool_calls"):
            # assume one tool call
            tc = resp["choices"][0]["message"]["tool_calls"][0]
            now = time.strftime("%H:%M:%S")
            # add flow: send result then format output
            await ctx.send(f"🛠 Calling {tc['function']['name']} → reply time={now}")
        else:
            await ctx.send("✅ " + resp["choices"][0]["message"]["content"])
    else:
        await ctx.send(f"❌ Status {st}")

@bot.command()
async def complete(ctx, *, prompt: str):
    """Text completion endpoint."""
    async with aiohttp.ClientSession() as s:
        payload = {"model":"your-model-id", "prompt":prompt, "max_tokens":100}
        st, resp = await http(s, "POST", COMP_URL, json=payload)
    if st==200:
        await ctx.send("📄 " + resp["choices"][0]["text"])
    else:
        await ctx.send(f"❌ Status {st}")

@bot.command()
async def embed(ctx, *, text: str):
    """Get embeddings."""
    async with aiohttp.ClientSession() as s:
        payload = {"model":"your-embed-model", "input":[text]}
        st, resp = await http(s, "POST", EMBED_URL, json=payload)
    if st==200:
        vec = resp["data"][0]["embedding"]
        await ctx.send(f"🔗 Embedding (len={len(vec)}): {vec[:5]}…")
    else:
        await ctx.send(f"❌ Status {st}")
