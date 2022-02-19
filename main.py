import discord
import requests
import json
import io
import aiohttp

client = discord.Client()

def get_image():
    rand_response = requests.get('https://danbooru.donmai.us/posts/random')
    response = requests.get(rand_response.url + '.json')
    json_data = json.loads(response.text)
    return json_data['file_url']
    
    

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('!random'):
        async with aiohttp.ClientSession() as session:
            async with session.get(get_image()) as resp:
                if resp.status != 200:
                    return await message.channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await message.channel.send(file=discord.File(data, 'random_img.png'))



client.run('OTQ0NDc4MTY2OTg1MTA1NDE4.YhCL1g.UJGq-_lkkchBl415Bq4M44pLcPI')