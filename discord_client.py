# Code took from https://note.com/jolly_dahlia842/n/n058c486b2e96

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


load_dotenv()
# Bot Access
TOKEN = os.getenv("DISCORD_TOKEN")  # Discord bot token
CMD_PREFIX = os.getenv("DISCORD_COMMAND_PREFIX", "!")  # Command Prefix
DIFY_URL = os.getenv("DIFY_API_URL")  # DIFY API Server URL
DIFY_KEY = os.getenv("DIFY_API_KEY")  # DIFY API Key

# Required intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)

# For continuation, The conversation_id is stored by channel
# In case the conversation has a larger time than 2hrs from
# the last message, then the conversation_id will be reset.
chat_ids = {}


@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')


@client.command()
async def chat(ctx, *, query: str):
    global chat_ids
    chat_room = str(ctx.channel.id)
    dt_now = datetime.now(ZoneInfo("Asia/Tokyo"))

    chat_id = ""
    if chat_room in chat_ids:
        if (dt_now - chat_ids[chat_room]["time"]) < timedelta(hours=2):
            chat_id = chat_ids[chat_room]["id"] 

    url = f'{DIFY_URL}/chat-messages'
    headers = {
        'Authorization': f'Bearer {DIFY_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'query': query,
        'response_mode': 'blocking',
        'user': str(ctx.author),
        'conversation_id': chat_id,
        'inputs': {},
    }

    if ctx.message.attachments:
        data["files"] = []

        for attached in ctx.message.attachments:
            ctype = attached.content_type.split("/", 1)[0]
            if ctype in ["image", "audio", "video"]:
                _data = {
                    "type": ctype,
                    "transfer_method": "remote_url",
                    "url": attached.url
                }
            elif ctype == "text":
                _data = {
                    "type": "document",
                    "transfer_method": "remote_url",
                    "url": attached.url
                }
            else:
                continue
            data["files"].append(_data)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                json_response = await response.json()
                answer = json_response.get('answer', 'No answer provided.')

                chat_id = json_response.get('conversation_id', '')
                if len(chat_id) > 0:
                    chat_ids[chat_room] = {
                        "id": chat_id,
                        "time": datetime.now(ZoneInfo("Asia/Tokyo"))
                    }
                await ctx.send(answer)
            else:
                error_message = await response.text()
                await ctx.send(f'API Error: {response.status}, Message: {error_message}')


client.run(TOKEN)
