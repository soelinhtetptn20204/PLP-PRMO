import discord; from discord.ext import commands
import os, sys, requests
from dotenv import load_dotenv
import math, cmath, numpy as np, cv2
import asyncio
import datetime
#import tensorflow as tf
#from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
#from cs50 import SQL
import json
import extra
from database import db

#channel names/id will change
RULES = 1166411281755025519
ENTRIES = 1166756190668206211
PROPOSAL = 1171098528156762183
JURY = 1171156729694785567

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
    db.execute("CREATE TABLE IF NOT EXISTS ? (psetID INTEGER PRIMARY KEY, topic TEXT, req_time TEXT NOT NULL, sub_time TEXT)", f"a{member.id}")
    db.execute("INSERT INTO approved (memberID, number) VALUES (?, 0)", member.id)
    ###create each user table foreign key included
    channel = bot.get_channel(ENTRIES)
    await channel.send(f"Please welcome {member.mention}.\
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
async def recommend(ctx, *, content):
    if not member_valid(ctx.author):
        return ctx.send(f"{ctx.author.mention}. Please rejoin the server to req problems")
    #implementation_left
    return

@bot.command(name="submit", help="$submit psetID followed by the image all at once")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def _submit(ctx, arg1: str, arg2: discord.Attachment):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server for submission")
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
    await ctx.send(f"{ctx.author.mention}. Success! Make sure u sent only one attachment.\
                   \nIf not, we recommend scanning all images, combining into a pdf, and sending again.")

###psetid number
@bot.command(name="hint_ask")
@commands.dm_only()
async def _hint_ask(ctx, psetid, number):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server for this service")
        return
    return

###psetid
@bot.command(name="pset_ask")
@commands.dm_only()
#check if admin or asking user has asking psetid valid in the database
async def _pset_ask(ctx, arg: int):
    problems = db.execute("SELECT * FROM psets WHERE psetID=? AND memberID=?", arg, ctx.author.id)
    if not admin_valid(ctx.author) or len(problems)==0:
        await ctx.send(f"{ctx.author.mention}. Asking psets denied.\
                        Make sure ur admin or u asked for only eligible psets u have asked in the past"); return
    #to_implement
    return

###one_of_the_topics
@bot.command(name="companion_match")
@commands.dm_only()
async def _companion_match(ctx, arg):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server for this service")
        return
    
###psetid memberid followed by numbers successful
@bot.command(name="success")
#check if admin
#only in dm_channel or submission channels
async def _success(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    if ctx.channel.id not in subm.values() or not isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send(f"{ctx.author.mention}. This command only allowed in submission channels or DM"); return
    """
    Pinned messages include number of psetID checked and success
    """
    return

#psetid 
@bot.command(name="pset_checked_ask")
@commands.dm_only()
async def _pset_checked_ask(ctx):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role to use this command"); return
    return

###memberid psetid followed by string of feedback
@bot.command(name="feedback_give")
@commands.dm_only()
async def _feedback_give(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!")
        return
    content = arg.split(" ", 2)
    mid, pid, feedback = (i.lower() for i in content)
    if not len(db.execute("SELECT * FROM ? WHERE psetID=?", f"a{mid}", pid)):
        await ctx.send("Invalid user or pset"); return
    user = await bot.fetch_user(int(mid))
    await user.send(f"Feedback by {ctx.author.name} on pset {pid}:")
    await user.send(feedback)
    return

###source rating topic problem
@bot.command(name="problem_add")
@commands.dm_only()
#check if admin
async def _problem_add(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!")
        return
    content = arg.split(" ", 3)
    if len(content) <4: 
        await ctx.send(f"{ctx.author.mention}. Not enough information for a problem"); return
    try: 
        source, rating, topic, problem = (i for i in content)
        rating = float(rating); source = extra.check_source(source.lower()); topic = extra.check_topic(topic.lower())
    except: await ctx.send("Invalid rating"); return
    if not source or len(db.execute("SELECT * FROM problems WHERE problemID=?", source)): 
        await ctx.send("Invalid problem source/ already exists."); return
    if not topic:
        await ctx.send("Invalid topic"); return
    db.execute("INSERT INTO problems (problemID, problem_statement, topic, p_rating) VALUES (?, ?, ?, ?)", source, rating, topic, problem)
    db.execute("CREATE TABLE IF NOT EXISTS ? (solving TEXT PRIMARY KEY, hints_used INTEGER, success INTEGER, checked_by TEXT)")
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} added a new problem {id} themed in {topic} rated {rating}")
    return

#problemID topic
@bot.command(name="problem_delete")
@commands.dm_only()
async def _problem_delete(ctx, id, topic):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    topic = extra.check_topic(topic)
    if not len(db.execute("SELECT * FROM problems WHERE problemID=? AND topic=?", id, topic)):
        await ctx.send(f"Invalid problemID or topic"); return
    db.execute("DELETE FROM problemID WHERE problemID=? AND topic=?", id, topic)
    db.execute("DROP TABLE ?", f"{topic}{id}")
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} deleted a problem {id} themed in {topic}")
    return

@bot.command(name="problem_tagged")
@commands.dm_only()
async def _problem_tagged(ctx):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You dont have the role for this command!")
        return

#problemID
@bot.command(name="problem_get")
@commands.dm_only()
async def _problem_get(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    content = db.execute("SELECT problem_statement from problems WHERE problemID=?", arg)
    if not len(content): 
        await ctx.send("Invalid problemID"); return
    content = content[0]['problem_statement']
    await ctx.send(content)
    return

@bot.command(name="hint_add")
@commands.dm_only()
#check if admin
async def _hint_add(ctx):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    return

@bot.command(name="hint_overwrite")
@commands.dm_only()
#check if admin
async def _hint_overwrite(ctx):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    return

#tag_name topic
@bot.command(name='tag_add')
@commands.dm_only()
@commands.is_owner()
async def _tag_add(ctx, name, topic: extra.check_topic):
    if not topic: 
        await ctx.send("Invalid topic"); return
    db.execute("INSERT INTO tags (name, topic) VALUES (?, ?)", name, topic)
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} added new tag: {name} in topic: {topic}")
    return

@bot.command(name="tag_delete")
@commands.is_owner()
@commands.dm_only()
async def _tag_delete(ctx, name, topic: extra.check_topic):
    if not topic:
        await ctx.send("Invalid topic"); return
    db.execute("DELETE FROM tags WHERE name=? AND topic=?", name, topic)
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} deleted the tag: {name} in topic: {topic}")
    return

#command followed by an image or suitable file
@bot.command(name="problem_propose")
@commands.dm_only()
async def _problem_propose(ctx, arg: discord.Attachment):
    if not member_valid(ctx.author):
       await ctx.send(f"{ctx.author.mention}. Please rejoin the server to propose problems."); return
    channel = await bot.fetch_channel(PROPOSAL)
    await channel.send(f"{arg.url.split('?')[0]}\
                       \nHere is the problem proposal by ID:{ctx.author.id} username:{ctx.author.name}")
    return

#userID 1_if_apporved_0_otherwise followed by any response/reason
@bot.command(name='response_proposal')
@commands.guild_only()
@commands.has_role("ADMIN")
async def _response_proposal(ctx, *, arg):
    if ctx.channel.id != PROPOSAL:
        await ctx.send(f"{ctx.author.mention}. This Command not allowed in this channel"); return
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server to propose problems."); return
    content = arg.split(" ", 2)
    if len(content) < 2:
        await ctx.send("Not enough information"); return
    if len(db.execute("SELECT * FROM members WHERE memberID=?", content[0])) == 0:
        await ctx.send("Invalid Member ID"); return
    try: content[1] = int(content[1])
    except: await ctx.send("1 for approval, 0 for disapproval"); return
    user = await bot.fetch_user(int(content[0])); response = content[2]
    jury = await bot.fetch_channel(JURY); a = "" if content else "not"
    to_send = f"{ctx.author.mention} did {a} approve a problem."
    await jury.send(to_send)
    await user.send(f"{to_send}.\n{response}")
    await ctx.send(f"{ctx.author.mention}. Make sure u added the latex'd version of problem and necessaries if approved.\
                   \nAfter that, ensure to delete the message of original problem proposal that you handled, to stay clean!!!")
    await ctx.author.send("problemID should be in the format [proposer_name][proposed_year][p][(n+1)^th_approved_by_that_user]")
    num = db.execute("SELECT number FROM approved WHERE memberID=?", content[0])[0]['number']
    await ctx.author.send(f"This user previously had {num} approvals")

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
        await ctx.send(f"{ctx.author.mention}, you do not have the priviledge to command this. Only owner can.")
    if isinstance(error, commands.MissingRole):
        await ctx.send(f'{ctx.author.mention}, you do not have the role to use this command')
    if isinstance(error, commands.MaxConcurrencyReached):
        await ctx.send(f'{ctx.author.mention}, bot is busy! Please retry in a minute')
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(f'{ctx.author.mention}, this command not allowed in DM')
    if isinstance(error, commands.PrivateMessageOnly):
        await ctx.send(f'{ctx.author.mention}, this command in DM only')

bot.run(token)
