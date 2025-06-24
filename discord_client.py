# Code took from https://note.com/jolly_dahlia842/n/n058c486b2e96

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp


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


@client.command()
async def chat(ctx, *, query: str):
    url = f'{DIFY_URL}/chat-messages'
    headers = {
        'Authorization': f'Bearer {DIFY_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'query': query,
        'response_mode': 'blocking',
        'user': 'user_identifier',
        'conversation_id': '',
        'inputs': {}
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                json_response = await response.json()
                answer = json_response.get('answer', 'No answer provided.')
                await ctx.send(answer)
            else:
                error_message = await response.text()
                await ctx.send(f'API Error: {response.status}, Message: {error_message}')


client.run(TOKEN)
