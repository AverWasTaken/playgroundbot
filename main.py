import discord
from discord.ext import commands
import random
import datetime
import openai
import asyncio
from openai import OpenAI
import os
from pathlib import Path
from discord import FFmpegPCMAudio
import json
from datetime import datetime

# Path to the users file
users_file_path = r'C:\Users\Administrator\Desktop\users.txt'

#Generate Random Colors For Embeds. 
TOKEN = ''
hex_characters = "0123456789ABCDEF"
embedfooter= 'developed with love, by ayvyr <3'
helpcmdsbot ='`.ping`>>check to see if the bots alive.\n`.activity`>>change the bots "playing" activity status.\n`.cgpt`>>use chatgpt within the bot\n`.ttsgpt`>>convert text to speech\n`.imggpt`>>make any image of your choosing.'
helpcmdsadmin ='`.ban`>>ban the user specified from server.\n`.kick`>>kick the user specified from server.\n`.timeout`>>time a user out for a specified time.\n`.purge`>>delete a specified number of messages.\n`.warn`>>warn a user.\n`.infractions`>>view a users infractions.\n`.clear`>>clear a users infractions. optinally, you can also specify what infracton to clear.'
user_threads = {}
assistant_id = ''
openai_api_key = ''
client_openai = openai.OpenAI(api_key=openai_api_key)
# ----------------------------------------------- #



# Define the bot, command prefix, and intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command('help')
client = OpenAI(api_key=openai_api_key)
# ----------------------------------------------- #

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# ----------------------------------------------- #

@bot.event
async def on_member_join(member):
    # Attempt to create a DM channel and send a welcome message
    try:
        if member.dm_channel is None:
            await member.create_dm()
        await member.dm_channel.send("Welcome to The Playground!")
    except Exception as e:
        print(f"Could not send a welcome message to {member.name}. Error: {e}")

    with open(users_file_path, 'a') as file:
        file.write(f'{member.id},{member.name}\n')
# ----------------------------------------------- #


# Member Leave Message
@bot.event
async def on_member_remove(member):
    user_name = None
    with open(users_file_path, 'r') as file:
        for line in file:
            user_id, name = line.strip().split(',')
            if int(user_id) == member.id:
                user_name = name
                break

    if user_name is None:
        print(f"User data not found for ID: {member.id}")
        return
      
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Generate a personalized goodbye message for a Discord user named {user_name}. They left a server called The Playground, and our goal is for user retention. Make them possibly want to join back by making your message convincing. The message should not be longer than a sentence or two. Include a funny joke that relates to them leaving and the server."}
            ]
        )
        
        goodbye_message = response.choices[0].message.content
        # Send the personalized message to the user's direct message
        try:
            if member.dm_channel is None:
                await member.create_dm()
            await member.dm_channel.send(goodbye_message)
        except discord.errors.Forbidden:
            print(f"Could not send a direct message to {user_name}. They might have their DMs disabled for non-friends or have no mutual server with the bot.")
    except Exception as e:
         print(f"An error occurred while trying to send a message to {user_name}. Error: {e}")

# ----------------------------------------------- #

# Define the "help" command
@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(title="executable commands", color=0xFFFFFF)
    embed.add_field(name='bot commands:', value=helpcmdsbot,  inline=False)
    embed.add_field(name = chr(173), value = chr(173))
    embed.add_field(name='admin commands', value=helpcmdsadmin,  inline=False)
    embed.set_footer(text=embedfooter)
    await ctx.send(embed=embed)
# ----------------------------------------------- #
#Ping Command
@bot.command(name='ping')
async def ping_cmd(ctx):
    await ctx.send('Pong!')
# ----------------------------------------------- #

#Ban Command
def has_any_role(ctx):
    allowed_roles = ['1179262457223589899', '1179262534382002246']
    user_roles = [str(role.id) for role in ctx.author.roles]  # Ensure the role IDs are strings
    return any(role_id in allowed_roles for role_id in user_roles)


@bot.command(name='ban')
@commands.check(has_any_role)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(title=f':white_check_mark: **{member.mention} has been banned for: {reason}, by administrator, {ctx.message.author.name}', color=0x2AFF00)
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(title=':question: **i cant do that LOL**', color=0xFF0000)
        await ctx.send(embed=embed)

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=':x: **specify someone next time idiot??**', color=0xFF0000)
        embed.set_footer(text=f'command ran by administrator, {ctx.message.author.name}')
        await ctx.send(embed=embed)
# ----------------------------------------------- #

#activity command
def has_any_role(ctx):
    allowed_roles = ['1179262457223589899', '1179262534382002246']
    user_roles = [str(role.id) for role in ctx.author.roles]  # Ensure the role IDs are strings
    return any(role_id in allowed_roles for role_id in user_roles)

@bot.command(name='activity')
@commands.check(has_any_role)
async def activity(ctx, *, text:str):
    activity = discord.Game(name=text, type=3)
    await bot.change_presence(activity=activity)
    embed = discord.Embed(title=f':white_check_mark: **game status changed to**',description=f'`Playing | {text}`', color=0x2AFF00)
    embed.set_footer(text=f'command ran by administrator, {ctx.message.author.name}')
    await ctx.send(embed=embed)

@activity.error
async def activ_error(ctx,error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':question: **insufficient permissions, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=':question: **specify an activity next time idiot??**', color=0xFF0000)
        embed.set_footer(text=f'command ran by administrator, {ctx.message.author.name}')
        await ctx.send(embed=embed)

# ----------------------------------------------- #
#Kick Command


def has_any_role(ctx):
    allowed_roles = ['1179262457223589899', '1179262534382002246']
    user_roles = [str(role.id) for role in ctx.author.roles]  # Ensure the role IDs are strings
    return any(role_id in allowed_roles for role_id in user_roles)


@bot.command(name='kick')
@commands.check(has_any_role)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(title=f':white_check_mark: **{member.mention} has been kicked for: {reason}, by administrator, {ctx.message.author.name}', color=0x2AFF00)
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(title=':question: **i cant do that LOL**', color=0xFF0000)
        await ctx.send(embed=embed)

@ban.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=':x: **specify someone next time idiot??**', color=0xFF0000)
        embed.set_footer(text=f'command ran by administrator, {ctx.message.author.name}')
        await ctx.send(embed=embed)

# ----------------------------------------------- #

#Warn Command
        
import json
import discord
from discord.ext import commands
from datetime import datetime

@bot.command(name='warn')
@commands.check(has_any_role)
async def warn(ctx, member: discord.Member, *, reason: str):
    # Define the path to your warnings file
    warnings_file_path = r'C:\Users\human\OneDrive\Desktop\Code\Playground\warnings.json'

    # Load existing warnings from the file
    try:
        with open(warnings_file_path, 'r') as file:
            try:
                warnings = json.load(file)
            except json.JSONDecodeError:  # Catch empty file or invalid JSON
                warnings = {}
                print("File is empty or contains invalid JSON. Starting with an empty dictionary.")
    except FileNotFoundError:
        warnings = {}
        print("File not found. Starting with an empty dictionary.")

    # Get the current timestamp
    current_time = datetime.utcnow().isoformat()

    # Structure the warning data
    warning_data = {
        'issuer': ctx.author.id,
        'reason': reason,
        'timestamp': current_time
    }

    # Add the warning to the member's list of warnings
    if str(member.id) in warnings:
        warnings[str(member.id)]['warnings'].append(warning_data)
        warnings[str(member.id)]['count'] += 1
    else:
        warnings[str(member.id)] = {
            'warnings': [warning_data],
            'count': 1
        }

    # Save the updated warnings back to the file
    with open(warnings_file_path, 'w') as file:
        json.dump(warnings, file, indent=4)

    # Confirmation message
    embed = discord.Embed(title=f':warning: Warned {member}', description=f'Reason: {reason}', color=0xFFA500)
    embed.set_footer(text=f'Warning issued by {ctx.author.name}')
    await ctx.send(embed=embed)

@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **Insufficient permissions**', color=0xFF0000)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=':question: **Missing required argument**', description='Please specify a user and a reason.', color=0xFF0000)
        await ctx.send(embed=embed)


# ----------------------------------------------- #
        
#Infractions Command
        
@bot.command(name='infractions')
@commands.check(has_any_role)
async def infractions(ctx, member: discord.Member):
    # Define the path to your warnings file
    warnings_file_path = r'C:\Users\human\OneDrive\Desktop\Code\Playground\warnings.json'

    # Try to load existing warnings from the file
    try:
        with open(warnings_file_path, 'r') as file:
            warnings = json.load(file)
    except FileNotFoundError:
        warnings = {}

    # Check if the member has any warnings
    if str(member.id) in warnings:
        member_warnings = warnings[str(member.id)]['warnings']
        warning_count = warnings[str(member.id)]['count']

        # Create an embed to display the warnings
        embed = discord.Embed(title=f'Infractions for {member}', color=0xFFA500)
        embed.add_field(name='Total Warnings', value=str(warning_count), inline=False)

        for idx, warning in enumerate(member_warnings, start=1):
            issuer = ctx.guild.get_member(warning['issuer'])
            issuer_name = issuer.name if issuer else 'Unknown'
            embed.add_field(name=f'Warning {idx}', value=f"Issuer: {issuer_name}\nReason: {warning['reason']}\nDate: {warning['timestamp']}", inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{member} has no infractions.")

@infractions.error
async def infractions_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(':x: **You do not have permission to use this command.**')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':question: **Please specify a user to check infractions for.**')
# ----------------------------------------------- #
        
#Clear Command
        
@bot.command(name='clear')
@commands.check(has_any_role)
async def clear(ctx, member: discord.Member, warning_number: int = None):
    # Define the path to your warnings file
    warnings_file_path = r'C:\Users\human\OneDrive\Desktop\Code\Playground\warnings.json'

    # Load existing warnings from the file
    try:
        with open(warnings_file_path, 'r') as file:
            warnings = json.load(file)
    except FileNotFoundError:
        warnings = {}

    # Check if the member has any warnings
    if str(member.id) in warnings:
        if warning_number is None:
            # Clear all warnings
            del warnings[str(member.id)]
            action_taken = "all warnings"
        else:
            # Clear specific warning, if it exists
            if 0 < warning_number <= len(warnings[str(member.id)]['warnings']):
                del warnings[str(member.id)]['warnings'][warning_number - 1]
                warnings[str(member.id)]['count'] -= 1
                action_taken = f"warning #{warning_number}"
            else:
                await ctx.send(f"Warning #{warning_number} does not exist for {member}.")
                return

        # Save the updated warnings back to the file
        with open(warnings_file_path, 'w') as file:
            json.dump(warnings, file, indent=4)

        await ctx.send(f"Cleared {action_taken} for {member}.")
    else:
        await ctx.send(f"{member} has no warnings to clear.")

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(':x: **You do not have permission to use this command.**')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(':question: **Please specify a user. Optionally, you can also specify a warning number to clear.**')

# ----------------------------------------------- #
        
#Timeout Command

def has_any_role(ctx):
    allowed_roles = ['1179262457223589899', '1179262534382002246']
    user_roles = [str(role.id) for role in ctx.author.roles]
    return any(role_id in allowed_roles for role_id in user_roles)

@bot.command(name='timeout')
@commands.check(has_any_role)
async def timeout(ctx, member: discord.Member, time: str, *, reason: str = None):
    try:
        time_multiplier = {'s': 1, 'm': 60, 'h': 3600}
        time_value, time_unit = int(time[:-1]), time[-1]
        
        if time_unit in time_multiplier:
            duration = datetime.timedelta(seconds=time_value * time_multiplier[time_unit])
            await member.timeout(duration, reason=reason)
            embed = discord.Embed(title=f':white_check_mark: {member} has been timed out for: {time_value}{time_unit}', color=0x2AFF00)
            embed.set_footer(text=f'command ran by administrator, {ctx.message.author.name}')
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=':question: **invalid format**', description='> **Invalid time format. Please use s (seconds), m (minutes), or h (hours).**', color=0xFF0000)
            embed.set_footer(text=f'command ran by administrator, {ctx.message.author.name}')
            await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(title=':question: **i cant do that LOL**', color=0xFF0000)
        await ctx.send(embed=embed)


@timeout.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=':question: **specify a time or user next time idiot??**', color=0xFF0000)
        embed.set_footer(text=f'command ran by administrator, {ctx.message.author.name}')
        await ctx.send(embed=embed)

# ----------------------------------------------- #

#timeout typo command
@bot.command(name='timout')
async def timout(ctx):
    embed = discord.Embed(title=':question: **did you mean, .timeout? :sob:**', color=0xFF0000)
    await ctx.send(embed=embed)
# ----------------------------------------------- #
@bot.command(name='purge')
@commands.check(has_any_role)
async def purge(ctx, num: int):
    await ctx.channel.purge(limit=num+1)
    embed = discord.Embed(title=f':bomb: **ive purged {num} messages**', color=0x2AFF00)
    embed.set_footer(text=f'command ran by administrator, {ctx.message.author.name}')
    await ctx.send(embed=embed)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title=':x: **invalid argument**', description='how many messages do you want to purge?', color=0xFF0000)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title=':x: **invalid argument**', description='how many messages do you want to purge?', color=0xFF0000)
        await ctx.send(embed=embed)
# ----------------------------------------------- #

#ChatGPT Command

def has_any_role(ctx):
    allowed_roles = ['1179290440978149386', '1179291074200617000']
    user_roles = [str(role.id) for role in ctx.author.roles]
    return any(role_id in allowed_roles for role_id in user_roles)

@bot.command(name='cgpt')
@commands.check(has_any_role)
async def cgpt(ctx, *, user_input: str):
    async with ctx.typing():
        user_message = user_input.strip()
        thread_id = user_threads.get(ctx.author.id)
        if not thread_id:
            thread = client_openai.beta.threads.create()
            thread_id = thread.id
            user_threads[ctx.author.id] = thread_id

        client_openai.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_message)
        run = client_openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

        run_status = "queued"
        while run_status != "completed":
            run_response = client_openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            run_status = run_response.status
            await asyncio.sleep(1)

        response = client_openai.beta.threads.messages.list(thread_id=thread_id)
        if response.data:
            for msg in response.data:
                if msg.role == 'assistant' and msg.content:
                    response_text = msg.content[0].text.value
                    chunk_size = 1900
                    for start in range(0, len(response_text), chunk_size):
                        chunk = response_text[start:start + chunk_size]
                        embed = discord.Embed(title="ChatGPT", description=chunk, color=0x00FF00)
                        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1176301401886961664/1178438917863784468/gpt.png?ex=657625c4&is=6563b0c4&hm=c9f9e90fd73ce6c73d15904f00a6023845cdca987690a459ab9c8c992212b10d&')
                        embed.set_footer(text="Made with ❤️, by ayvyr", icon_url='https://cdn.discordapp.com/attachments/1131259938291847229/1176595477362393219/1736259-200.png?ex=656f70ed&is=655cfbed&hm=abcc183e0e1efa7f56af92b48fe0fbe8d2db88203628805c8c62ce8d2b650669&')
                        await ctx.send(embed=embed)
                break
        else:
            await ctx.send("No response message found.")
@cgpt.error
async def cgpt_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions to use ChatGPT, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)
# ----------------------------------------------- #  

#ImgGPT Command 
@bot.command(name="imggpt")
@commands.check(has_any_role)
async def imggpt(ctx, *, user_input: str):
    try:
        async with ctx.typing():
            response = client.images.generate(
                model="dall-e-3",
                prompt=user_input,
                size="1024x1024",
                quality="standard",
                n=1,
            )
        image_url = response.data[0].url
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send("Sorry, I can't generate that!")


@imggpt.error
async def imggpt_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions to use ChatGPT Image Creation, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)


# ----------------------------------------------- #
        
#TTS Gpt Command

@bot.command(name="ttsgpt")
@commands.check(has_any_role)
async def ttsgpt(ctx, *, user_input: str):
    try:
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=user_input  # Use the user's input here
        )

        response.stream_to_file(speech_file_path)

        await ctx.send(file=discord.File(speech_file_path))  # Send the file to the Discord channel

    except Exception as e:  # Handle any exceptions
        await ctx.send(f"An error occurred: {e}")



@ttsgpt.error
async def ttsgpt_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions to use ChatGPT Image Creation, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)

# ----------------------------------------------- #

#Vc Talk Command

@bot.command(name="vctalk")
@commands.check(has_any_role)
async def vctalk(ctx, *, user_input: str):
    try:
        # Ensure the user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You are not connected to a voice channel.")
            return

        voice_channel = ctx.author.voice.channel

        # Generate the TTS file
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=user_input
        )
        response.stream_to_file(speech_file_path)

        # Join the voice channel and play the audio
        vc = await voice_channel.connect()
        vc.play(FFmpegPCMAudio(executable="C:\\Users\\Administrator\\Desktop\\ffmpeg-6.1.1-essentials_build\\bin\\ffmpeg.exe", source=str(speech_file_path)))

        # Wait until the audio is done playing
        while vc.is_playing():
            await asyncio.sleep(1)

        # Disconnect after the audio has finished playing
        await vc.disconnect()

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        if vc.is_connected():
            await vc.disconnect()

@vctalk.error
async def vctalk(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions to use ChatGPT Image Creation, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)


@bot.command(name='cgpts')
@commands.check(has_any_role)
async def cgpts(ctx, *, user_input: str):
    async with ctx.typing():
        user_message = user_input.strip()
        thread_id = user_threads.get(ctx.author.id)
        if not thread_id:
            thread = client_openai.beta.threads.create()
            thread_id = thread.id
            user_threads[ctx.author.id] = thread_id

        client_openai.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_message)
        run = client_openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

        run_status = "queued"
        while run_status != "completed":
            run_response = client_openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            run_status = run_response.status
            await asyncio.sleep(1)

        response = client_openai.beta.threads.messages.list(thread_id=thread_id)
        if response.data:
            for msg in response.data:
                if msg.role == 'assistant' and msg.content:
                    response_text = msg.content[0].text.value
                    chunk_size = 1900
                    for start in range(0, len(response_text), chunk_size):
                        chunk = response_text[start:start + chunk_size]

                    try:
                        speech_file_path = Path(__file__).parent / "speech.mp3"
                        response = client.audio.speech.create(
                            model="tts-1-hd",
                            voice="onyx",
                            input=chunk  # Use the user's input here
                        )

                        response.stream_to_file(speech_file_path)

                        await ctx.send(file=discord.File(speech_file_path)) 
                    except Exception as e:
                        await ctx.send(f"An error occurred: {e}") 
                break
        else:
            await ctx.send("No response message found.")

@cgpts.error
async def cgpts_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **insufficient permissions to use ChatGPT, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)



@bot.command(name='vcgpt')
@commands.check(has_any_role)
async def vcgpt(ctx, *, user_input: str):
    try:
        # Ensure the user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You are not connected to a voice channel.")
            return
        
        voice_channel = ctx.author.voice.channel

        async with ctx.typing():
            user_message = user_input.strip()
            thread_id = user_threads.get(ctx.author.id)
            if not thread_id:
                thread = client_openai.beta.threads.create()
                thread_id = thread.id
                user_threads[ctx.author.id] = thread_id

            client_openai.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_message)
            run = client_openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

            run_status = "queued"
            while run_status != "completed":
                run_response = client_openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                run_status = run_response.status
                await asyncio.sleep(1)

            response = client_openai.beta.threads.messages.list(thread_id=thread_id)
            if response.data:
                for msg in response.data:
                    if msg.role == 'assistant' and msg.content:
                        response_text = msg.content[0].text.value
                        chunk_size = 1900  # Assuming limit related to Discord message length
                        for start in range(0, len(response_text), chunk_size):
                            chunk = response_text[start:start + chunk_size]

                        # Generate the TTS file
                        speech_file_path = Path(__file__).parent / "speech.mp3"
                        response = client.audio.speech.create(
                            model="tts-1-hd",
                            voice="nova",  # or "onyx", choose the preferred voice
                            input=chunk  # Use the user's input here
                        )
                        response.stream_to_file(speech_file_path)
                        vc = await voice_channel.connect()
                        # Play the audio in the voice channel
                        vc.play(FFmpegPCMAudio(executable="C:\\Users\\Administrator\\Desktop\\ffmpeg-6.1.1-essentials_build\\bin\\ffmpeg.exe", source=str(speech_file_path)))

                        # Wait until audio is done playing
                        while vc.is_playing():
                            await asyncio.sleep(1)
                        break
            else:
                await ctx.send("No response message found.")
        await vc.disconnect()  # Disconnect after playing message

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        if vc and vc.is_connected():
            await vc.disconnect()

@vcgpt.error
async def vcgpt_error(ctx, error):
    # Handle insufficient permissions in the same way as before
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: **Insufficient permissions to use vcgpt, nice try lol**', color=0xFF0000)
        embed.set_footer(text=f'Command ran by user, {ctx.message.author.name}')
        await ctx.send(embed=embed)

# Run the bot

bot.run(TOKEN)
