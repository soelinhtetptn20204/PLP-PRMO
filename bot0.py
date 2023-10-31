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
from extra import *

#channel names/id will change
RULES = 1166411281755025519
ENTRIES = 1166756190668206211
ALGEBRA = 1166770207386255470
COMBI = 1166770238168248411
GEOMETRY = 1166770259550797934
NUMTHEO = 1166770259550797934

ratings = {
    'IMO-er': 4,
    'TST': 3,
    'MOMC_Sr': 2.5
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
           problem_statement TEXT UNIQUE NOT NULL, source TEXT, topic TEXT NOT NULL,\
           tags TEXT, p_rating REAL)")

db.execute("CREATE TABLE IF NOT EXISTS tags (tagID INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, topic TEXT NOT NULL)")

db.execute("CREATE TABLE IF NOT EXISTS contests (abbr TEXT, name TEXT)")

db.execute("CREATE TABLE IF NOT EXISTS hints (p_id INTEGER PRIMARY KEY, hint_1 TEXT, hint_2 TEXT, hint_3 TEXT)")

#each problem, user and tags
db.execute("CREATE TABLE IF NOT EXISTS each_problem (solving TEXT PRIMARY KEY, hints_used INTEGER, success INTEGER, checked_by TEXT)")

db.execute("CREATE TABLE IF NOT EXISTS each_user (requested INTEGER NOT NULL, req_time TEXT NOT NULL, sub_time TEXT)")

db.execute("CREAT TABLE IF NOT EXISTS each_tag (p_id INTEGER PRIMARY KEY, p_rating REAL)")

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
    #await member.send(member.roles[1].name)
    if channel == RULES:
        if not db.execute("SELECT level FROM members WHERE memberID=?", f"{member.id}")[0]['level']:
            lvl = member.roles[1].name
            med = [ratings[lvl]]*4
            db.execute("UPDATE members SET m_rating=?, level=? WHERE memberID=?", f"{med}", lvl, member.id)
            await member.send("Great. Your role has been set. Please don't change the role.\
                              \nIf u did or intend to, please inform the administrators.")

@bot.event 
async def on_member_remove(member):
    db.execute("UPDATE members SET activated=0 WHERE memberID=?", member.id)

@bot.command(name="recommend", help="Just uses $recommend in DM")
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
#@commands.cooldown(1, 250, commands.BucketType.default)
async def _recommend(ctx):
    """
    Planning to change with language processing for more convenience.
    """
    user = ctx.author
    if not member_valid(user):
        await ctx.send("Please rejoin the server to request problems.")
        return
    query = {
        "Topic u'd like to do": "",
        "How many questions": "",
        "Problem-theme Tags": "comma ',' or 'and' for union",
        "Difficulty rating": f"You can refer to problem rating numbers and usage in the <#{RULES}>."
    }
    for q in query:
        for i in range(3):
            await ctx.send(f"{q}? {query[q]}")
            try:
               message = await bot.wait_for("message", timeout=60)
            except:
               await ctx.send("Time out. Please msg me $recommend for problem req")
            if check1(message.content, q) not in {'1','2','3','4','5'}:
                query[q] = message.content
                break
            if i == 2:
               await ctx.send("Try again. Message me $recommend for problem req")
               return
    return

@bot.command(name="level_rating_change")
@commands.has_role("ADMIN")
async def _level_rating_changes(ctx, arg): 
    #to_implement
    return

@bot.command(name="problem_add")
@commands.has_role("ADMIN")
async def _problem_add(ctx):
    return

@bot.command(name="hint_add")
@commands.has_role("ADMIN")
async def _hint_add(ctx):
    return

@bot.command(name='tag_add')
@commands.has_role("ADMIND")
async def _tag_add(ctx):
    return

@bot.command(name="delete_invite_links")
@commands.has_role("ADMIN")
async def _delete_invite_links(ctx):
    guild = ctx.guild
    for invite in await guild.invites():
        await invite.delete()
    await ctx.send("Done Deleting")

@bot.command(name="nlp_increase")
@commands.has_role("ADMIN")
async def _nlp_increase(ctx):
    return

#Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the role to use this command')
    if isinstance(error, commands.MaxConcurrencyReached):
        await ctx.author.send('Bot is busy! Please retry in a minute')

bot.run(token)
