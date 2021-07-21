import asyncio
import discord
import time
import random
from discord.ext import commands
from qotd_data import QotdData
from qotd_data import SECONDS_PER_DAY

TOKEN = open('TOKEN.txt').readline()
bot = commands.Bot(command_prefix='.tns ')
DATA = None

@bot.event
async def on_ready():
    global DATA
    DATA = QotdData()
    print('TNS Qotd Bot is Ready!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    handle_message(message)
    await bot.process_commands(message)

@bot.command(name='discussion')
@commands.has_role('QOTD Master')
async def set_discussion_channel(ctx):
    guild_id = ctx.message.guild.id
    channel_id = ctx.message.channel.id
    DATA.set_discussion_channel(guild_id, channel_id)
    embed = discord.Embed(title="QOTD Bot", description="Set this channel to be the new discussion channel!", color=0x32cd32)
    await ctx.send(embed=embed)

@bot.command(name='suggestions')
@commands.has_role('QOTD Master')
async def set_suggestion_channel(ctx):
    guild_id = ctx.message.guild.id
    channel_id = ctx.message.channel.id
    DATA.set_suggestion_channel(guild_id, channel_id)
    embed = discord.Embed(title="QOTD Bot", description="Set this channel to be the new suggestions channel!", color=0x32cd32)
    await ctx.send(embed=embed)

@bot.command(name='pick')
@commands.has_role('QOTD Master')
async def pick_suggestion(ctx, member: discord.Member):
    guild_id = ctx.message.guild.id
    settings = DATA.get_settings_for_guild(guild_id)
    try:
        picked_user = await bot.fetch_user(member.id)
        DATA.add_user_points(guild_id, picked_user, settings['points_for_picked_suggestion'])
        last_suggestion = DATA.get_last_suggestion(guild_id, picked_user)
    except Exception:
        await ctx.send(f'''Unknown user!''')
        return
    await ctx.send(f'''Picked a suggestion from {picked_user.mention}! Their last suggestion was: {last_suggestion['content']}''')

@bot.command(name='remove_points')
@commands.has_role('QOTD Master')
async def remove_points(ctx, member: discord.Member, points: int):
    guild_id = ctx.message.guild.id
    try:
        picked_user = await bot.fetch_user(member.id)
        DATA.add_user_points(guild_id, picked_user, -points)
    except Exception:
        await ctx.send(f'''Error removing points''')
        return
    await ctx.send(f'''Removed {points} point(s) from {picked_user.mention}!''')

@bot.command(name='points')
async def get_points(ctx):
    guild_id = ctx.message.guild.id
    user = ctx.message.author
    points = DATA.get_user_points(guild_id, user)
    reply = f"You have {points} point"
    if points != 1:
        reply += "s"
    reply += "!"
    embed = discord.Embed(title='QOTD Bot', description=reply, color=0x32cd32)
    await ctx.send(embed=embed)

@bot.command(name='leaderboard')
async def get_leaderboard(ctx):
    guild_id = ctx.message.guild.id
    users = DATA.get_users(guild_id)
    sorted_users = sorted(list(users.keys()), key=lambda u : users[u]['points'])
    sorted_users.reverse()
    desc = f"Top {len(sorted_users[:10])} QOTD answerers:\n"
    for i, user_id in enumerate(sorted_users[:10]):
        desc += f"{i + 1}: **{await bot.fetch_user(int(user_id))}** - {users[user_id]['points']} point(s)\n"
    
    embed = discord.Embed(title='QOTD Bot', description=desc, color=0x32cd32)
    await ctx.send(embed=embed)

@bot.command(pass_context=True, name="thegame")
async def the_game(ctx, channel: discord.channel=None):
    min_time = 15*60
    max_time = 720*60
    if channel is None:
        channel = ctx.message.channel
    while True:
        await bot.get_channel(channel.id).send('The Game')
        await asyncio.sleep(random.randint(min_time, max_time))

def handle_discussion(message: discord.Message):
    guild_id = message.guild.id
    last_message = DATA.get_last_answer(guild_id, message.author)
    current_time = time.time()
    settings = DATA.get_settings_for_guild(guild_id)
    if last_message is None or current_time - last_message['time'] >= settings['time_between_discussions']:
        DATA.update_user_answer(guild_id, message.author, message)
        points_to_add = settings['points_for_discussion']
        DATA.add_user_points(guild_id, message.author, points_to_add)

def handle_suggestion(message):
    guild_id = message.guild.id
    last_message = DATA.get_last_suggestion(guild_id, message.author)
    current_time = time.time()
    settings = DATA.get_settings_for_guild(guild_id)
    if last_message is None or current_time - last_message['time'] >= settings['time_between_suggestion']:
        DATA.update_user_suggestion(guild_id, message.author, message)
        points_to_add = settings['points_for_suggestion']
        DATA.add_user_points(guild_id, message.author, points_to_add)

def handle_message(message):
    guild_id = message.guild.id
    channel_id = message.channel.id
    if message.content.lower().startswith('qotd -'):
        if channel_id == DATA.get_discussion_channel(guild_id):
            handle_discussion(message)
        if channel_id == DATA.get_suggestion_channel(guild_id):
            handle_suggestion(message)

bot.run(TOKEN)