import discord; from discord.ext import commands
import os, sys, requests
from dotenv import load_dotenv
import math, cmath, numpy as np, cv2
import asyncio
import datetime
#import tensorflow as tf
#from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
import json
import extra

#channel names/id will change
RULES = 1166411281755025519
ENTRIES = 1166756190668206211

subm = {
"A": 1166770207386255470,
"C": 1166770238168248411,
"G": 1166770259550797934,
"N": 1166770259550797934
}

ratings = {
    'ADMIN': 4,
    'IMO-er': 4,
    'TST': 3,
    'MOMC_Sr': 2.5,
    'MOMC_Jr': 2
}

#errors
with open("error_code.txt") as f:
    errors = f.read()
errors = json.loads(errors)

### DATA BASE ***
db = SQL("sqlite:///test.db")

db.execute("CREATE TABLE IF NOT EXISTS members (memberID TEXT PRIMARY KEY,\
             level TEXT, m_rating TEXT, activated INTEGER)")

db.execute("CREATE TABLE IF NOT EXISTS problems (problemID INTEGER PRIMARY KEY AUTOINCREMENT,\
           problem_statement TEXT UNIQUE NOT NULL, source TEXT, topic TEXT NOT NULL, p_rating REAL)")

db.execute("CREATE TABLE IF NOT EXISTS psets (psetID INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, memberID TEXT,\
            p1 INTEGER, p2 INTEGER, p3 INTEGER, p4 INTEGER, p5 INTEGER)") 

db.execute("CREATE TABLE IF NOT EXISTS tags (tagID INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, topic TEXT NOT NULL)")

db.execute("CREATE TABLE IF NOT EXISTS hints (p_id INTEGER PRIMARY KEY, hint_1 TEXT, hint_2 TEXT, hint_3 TEXT)")

#each problem, user and tags
db.execute("CREATE TABLE IF NOT EXISTS each_problem (solving TEXT PRIMARY KEY, hints_used INTEGER, success INTEGER, checked_by TEXT)")
#format {topic}{id}

db.execute("CREATE TABLE IF NOT EXISTS each_user (psetID INTEGER PRIMARY KEY, topic TEXT, req_time TEXT NOT NULL, sub_time TEXT)") 
#format a{userID}

db.execute("CREATE TABLE IF NOT EXISTS each_tag (p_id INTEGER PRIMARY KEY, p_rating REAL)") 
#format {topic}{tagID}

#users' query
db.execute("CREATE TABLE IF NOT EXISTS queries (prompt TEXT)")
### DATA BASE ***


load_dotenv()
token = os.getenv('TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '$', intents=intents)
#client = discord.Client(intents=intents)

FID = "Feauture still in Development!!!"

def member_valid(member):
    to_check = db.execute("SELECT * FROM members WHERE memberID=? AND activated=1", member.id)
    return len(to_check)

def admin_valid(member):
    to_check = db.execute("SELECT * FROM members WHERE memberID=? AND level=? AND activated=1", member.id, 'ADMIN')
    return len(to_check)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is connected to Discord')

@bot.event
async def on_member_join(member):
    check = db.execute("SELECT * FROM members where memberID=?", f"{member.id}")
    if len(check): 
        await member.send("Welcome back!")
        db.execute("UPDATE members SET activated = 1 WHERE memberID=?", f"{member.id}")
        return
    await member.send(f"Welcome to IMO testing! Don't forget to react to any one msg in <#{RULES}> to get started.") 
    db.execute("INSERT INTO members (memberID, activated) VALUES (?, 1)", f"{member.id}")
    channel = bot.get_channel(ENTRIES)
    await channel.send(f"Please welcome @{member.name}.\
                       \nEnjoy problem solving!")

@bot.event
async def on_raw_reaction_add(payload):
    member = payload.member
    channel = payload.channel_id
    if channel == RULES:
        lvl = member.roles[1].name
        med = [ratings[lvl]]*4
        if not db.execute("SELECT level FROM members WHERE memberID=?", f"{member.id}")[0]['level']:
            await member.send("Great. Your role has been set. Please don't change the role.\
                              \nIf u did or intend to, please inform the administrators.")
        db.execute("UPDATE members SET m_rating=?, level=? WHERE memberID=?", f"{med}", lvl, member.id)

@bot.event 
async def on_member_remove(member):
    db.execute("UPDATE members SET activated=0 WHERE memberID=?", member.id)

@bot.command(name="recommend")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def recommend(ctx):
    if not member_valid(ctx.author):
        return ctx.send("Please rejoin the server to req problems")
    #implementation_left
    return

@bot.command(name="submit", help="$submit psetID followed by the image all at once")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def _submit(ctx, arg1: str, arg2: discord.Attachment):
    if not member_valid(ctx.author):
        await ctx.send("Please rejoin the server for submission")
        return
    top = 'A'
    """
    top = db.execute("SELECT topic FROM ? WHERE psetID = ?", f"a{ctx.author.id}", int(arg1))
    if len(top) == 0:
        await ctx.send("Invalid pset ID. Try again. $submit psetID followed by the image all at once")
        return 
    top = top[0]['topic']
    """
    channel = await bot.fetch_channel(subm[top])
    await channel.send(f"{arg2.url.split('?')[0]}\
                       \npsetID: {arg1}, submittor: {ctx.author.name}")
    await ctx.send("Success! Make sure u sent only one attachment.\nOtherwise, we recommend scanning all images, combining into a pdf, and sending again.")

###one_of_the_topics
@bot.command(name="match_companion")
@commands.dm_only()
async def _match_companion(ctx, arg):
    if not member_valid(ctx.author):
        await ctx.send("Please rejoin the server for this service")
        return

###psetid
@bot.command(name="ask_pset")
#check if admin
async def _ask_pset(ctx, arg: int):
    #to_implement
    if not admin_valid(ctx.author):
        await ctx.send("You don't have the role for this command!")
        return
    return

###psetid memberid followed by numbers successful
@bot.command(name="success")
#check if admin
async def _success(ctx, psetid, memberid):
    if not admin_valid(ctx.author):
        await ctx.send("You don't have the role for this command!")
        return
    return

###memberif psetid followed by string of feedback
@bot.command(name="give_feedback")
#check if admin
async def _give_feedback(ctx, memberid, psetid):
    if not admin_valid(ctx.author):
        await ctx.send("You don't have the role for this command!")
        return
    return

###
@bot.command(name="level_rating_change")
@commands.guild_only()
@commands.has_role("ADMIN")
async def _level_rating_changes(ctx, arg1, arg2, arg3): 
    if not admin_valid(ctx.author):
        await ctx.send("You don't have the role for this command!")
        return
    #to_implement
    return

@bot.command(name="problem_add")
#check if admin
async def _problem_add(ctx):
    if not admin_valid(ctx.author):
        await ctx.send("You don't have the role for this command!")
        return
    return

@bot.command(name="hint_add")
#check if admin
async def _hint_add(ctx):
    if not admin_valid(ctx.author):
        await ctx.send("You don't have the role for this command!")
        return
    return

@bot.command(name='tag_add')
#check if admin
async def _tag_add(ctx):
    if not admin_valid(ctx.author):
        await ctx.send("You don't have the role for this command!")
        return
    return

###connect member of similar level

@bot.command(name="delete_invite_links")
@commands.guild_only()
@commands.has_role("ADMIN")
async def _delete_invite_links(ctx):
    guild = ctx.guild
    for invite in await guild.invites():
        await invite.delete()
    await ctx.send("Done Deleting")

@bot.command(name="nlp_increase")
@commands.is_owner()
async def _nlp_increase(ctx):
    return

#Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.author.send("You do not have the priviledge to command this. Only owner can.")
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.author.send('You do not have the role to use this command or wrong server/channel')
    if isinstance(error, commands.MaxConcurrencyReached):
        await ctx.author.send('Bot is busy! Please retry in a minute')
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.author.send('This command not allowed in DM')
    if isinstance(error, commands.PrivateMessageOnly):
        await ctx.author.send('This command in DM only')

bot.run(token)
