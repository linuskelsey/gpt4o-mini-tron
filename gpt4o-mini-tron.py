import discord
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

# Discord and OpenAI API tokens
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
OAIclient = OpenAI(api_key=OPENAI_API_KEY)

# Set up Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Function to split messages exceeding 2000 characters
def split_message(message, limit=2000):
    return [message[i:i+limit] for i in range(0, len(message), limit)]

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}!')

@client.event
async def on_message(message):
    # Avoid responding to the bot's own messages
    if message.author == client.user:
        return

    # Check if message is in the specified channel
    if str(message.channel.id) != CHANNEL_ID:
        return

    # Only respond if message starts with a command trigger, e.g., '!ask'
    if message.content.startswith('!ask'):

        try:
            prompt = message.content[len('!ask '):].strip()  # Remove the command trigger from the prompt
            response = OAIclient.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.choices[0].message.content

            # Check and split if the response is too long
            if len(response_text) > 2000:
                message_parts = split_message(response_text)
                for part in message_parts:
                    await message.channel.send(part)
            else:
                await message.channel.send(response_text)
                
        except Exception as e:
            await message.channel.send(f"Error: {str(e)}")

# Run the bot
client.run(DISCORD_TOKEN)