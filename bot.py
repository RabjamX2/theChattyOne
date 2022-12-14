import openai
import discord
from config import openAIToken, discordBotToken, channelID

# Set up the OpenAI API key
openai.api_key = openAIToken

# Create a new Discord client
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

# Define the target Discord channel
channel_id = channelID

# Triggers
imageTrigger = "image of "
closeTrigger = "bye"

# Handle messages received in the target Discord channel
@client.event
async def on_message(message):
    # To ignore itself
    if message.author == client.user:
        return

    if message.channel.id == channel_id or message.channel.id == 1052391367449522296:
        if message.author == "RabjamX2#1936": 
            if message.content == closeTrigger:
                await client.close()
    try:
        # Check if the message content is flagged by the moderation model
        flagged = openai.Moderation.create(
            input=message.content
        ).results[0]

        # If the message is flagged, do not generate a response
        if flagged["flagged"]:
            if message.channel.id == channel_id or message.channel.id == 1052392685568282675:
                for flag in flagged["categories"]:
                    if flagged["categories"][flag]:
                        if flag == "sexual":
                            await message.channel.send(f"Yo {message.author.mention} , stop being horny... You down bad man")
                        else:
                            await message.channel.send(f"Yo {message.author.mention} , stop it with the talks of {flag}")
        else:
            if message.content.startswith(imageTrigger):
                response = openai.Image.create(
                    prompt=message.content[len(imageTrigger):],
                    n=1,
                    size="1024x1024"
                ).data[0].url

                await message.channel.send(response)
            else:
                if message.channel.id == channel_id or message.channel.id == 1052392685568282675:
                    # Generate a response using the chatGPT model
                    response = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=message.content,
                        max_tokens=3024,
                        n=1,
                        #Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
                        temperature=0.9
                    ).choices[0].text

                    # Send the response to the Discord channel
                    await message.channel.send(response)
    except Exception as e:
        # Send a message to the Discord channel with the error message and the user who caused the error
        await message.channel.send(f"{message.author.mention}, you got me fucked up. Error: {e}")


# Run the Discord client
client.run(discordBotToken)