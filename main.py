# A custom coded discord bot for the playground. desgined and made with love by ayvyr

import discord
from discord.ext import commands
import random
import datetime
import openai
import asyncio

 
TOKEN = ''
embedfooter= 'developed with love, by ayvyr <3'
helpcmdsbot ='`.ping`>>check to see if the bots alive.\n`.activity`>>change the bots "playing" activity status.\n`.cgpt`>>use chatgpt within the bot'
helpcmdsadmin ='`.ban`>>ban the user specified from server.\n`.kick`>>kick the user specified from server.\n`.timeout`>>time a user out for a specified time.\n`.purge`>>delete a specified number of messages.'
user_threads = {}
assistant_id = ''
openai_api_key = ''
client_openai = openai.OpenAI(api_key=openai_api_key)
# ----------------------------------------------- #



# Define the bot, command prefix, and intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command('help')
# ----------------------------------------------- #

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

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
#Activity command
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

@kick.error
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

#Timeout typo command
@bot.command(name='timout')
async def timout(ctx):
    embed = discord.Embed(title=':question: **did you mean, .timeout? :sob:**', color=0xFF0000)
    await ctx.send(embed=embed)


# ----------------------------------------------- #
#Purge Command
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
# Run the bot
bot.run(TOKEN)


