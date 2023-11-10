import discord; from discord.ext import commands
import os, sys, requests
from dotenv import load_dotenv
import math, cmath, numpy as np, cv2
import asyncio
from datetime import datetime
#import tensorflow as tf
#from PIL import Image
#from cs50 import SQL
import json
import extra
import re
from database import db

#channel names/id will change
RULES = 1166411281755025519
ENTRIES = 1166756190668206211
PROPOSAL = 1171098528156762183
JURY = 1171156729694785567

subm = {
"a": 1166770207386255470,
"c": 1166770238168248411,
"g": 1166770259550797934,
"n": 1166770259550797934
}

toi = {
    'a': 0,
    'c': 1,
    'g': 2,
    'n': 3
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

FORMAT = "\begin{center}\n{\large Pset id - topic}\n\end{center}\n\begin{enumerate}\n"

load_dotenv()
token = os.getenv('TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '$', intents=intents)
#client = discord.Client(intents=intents)

FID = "Feauture still in Development!!!"

def member_valid(member):
    to_check = db.execute("SELECT memberID FROM members WHERE memberID=? AND activated=1", member.id)
    return len(to_check)

def admin_valid(member):
    to_check = db.execute("SELECT memberID FROM members WHERE memberID=? AND level=? AND activated=1", member.id, 'ADMIN')
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
    db.execute("CREATE TABLE IF NOT EXISTS ? (psetID INTEGER PRIMARY KEY, topic TEXT, sub_time TEXT\
               CONSTRAINT constraint_hint FOREIGN KEY (problemID) REFERENCES problems(problemID) ON DELETE CASCADE)", f"a{member.id}")
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

@bot.command(name="hey")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def recommend(ctx, *, content):
    if not member_valid(ctx.author):
        return ctx.send(f"{ctx.author.mention}. Please rejoin the server to req problems")
    default_num = 3
    default_rating = eval(db.execute("SELECT m_rating FROM members WHERE memberID=?", ctx.author.id)[0]['m_rating'])
    content = extra.text_transform(content.strip().lower())
    #transform the text so that all punctuation symbols and numbers are spaced at least once
    #implementation_left
    return

@bot.command(name = "recommend")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def recommend(ctx, *, content):
    ### IF NLP MODEL DOESNT WORK ###
    return

@bot.command(name="submit", help="$submit psetID followed by the image all at once")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def _submit(ctx, arg1: str, arg2: discord.Attachment):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server for submission")
        return
    top = 'a'; arg1 = arg1.lower()
    """
    top = db.execute("SELECT topic FROM ? WHERE psetID = ?", f"a{ctx.author.id}", arg1)
    if len(top) == 0:
        await ctx.send("Invalid pset ID. Try again. $submit psetID followed by the image all at once")
        return 
    top = top[0]['topic']
    now = datetime.now.strftime("%d/%m/%Y, %H:%M")
    db.execute("UPDATE ? SET sub_time=? WHERE psetID=?", f"a{ctx.author.id}", {now}, arg1)
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
    problemid = db.execute("SELECT ? FROM psets WHERE problemID=?", psetid.lower(), f"p{number}")
    if len(problemid) == 0 or not problemid[0][f'p{number}']:
        await ctx.send("Invalid PsetID or number")
    problemid = problemid[0][f'p{number}']
    hints = db.execute("SELECT hint_1, hint_2, hint_3 FROM hints WHERE problemID=?", problemid)[0]
    hints = {hint: hints[hint] for hint in hints if hints[hint]}
    if len(hints) == 0:
        await ctx.send("Sorry, not hint available for this problem. Feel free to discuss with others by posting a forum"); return
    to_send = f"Hints for {psetid} no {number}\n"
    for hint in hints:
        to_send += f"<||{hint}: {hints[hint]}\n||>"
    await ctx.send(to_send)
    return

###psetid
@bot.command(name="pset_ask")
@commands.dm_only()
#check if admin or asking user has asking psetid valid in the database
async def _pset_ask(ctx, arg):
    arg1 = arg1.lower()
    problems = db.execute("SELECT * FROM psets WHERE psetID=? AND memberID=?", arg, ctx.author.id)
    if not admin_valid(ctx.author) or len(problems)==0:
        await ctx.send(f"{ctx.author.mention}. Asking psets denied.\
                        Make sure ur admin or u asked for only eligible psets u have asked in the past"); return
    problemid = db.execute("SELECT topic, p1, p2, p3, p4, p5 FROM psets WHERE psetID=?", arg)
    if not len(problemid):
        await ctx.send("Invalid Pset"); return
    topic = problemid[0].pop('topic')
    problemid = [problemid[0][f'p{num}'] for num in problemid if problemid[0][f'p{num}']]
    to_send = FORMAT.replace('id', arg).replace('topic', topic)
    for id in problemid:
        content = db.execute("SELECT problem_statement FROM problems WHERE problemID=?", id)
        if len(content) == 0: content = "\item This problem no longer exists.\n"
        else: content = content[0]['problem_statement']
        to_send += f"\item {content}\n"
    to_send += "\end{enumerate}\n"
    await ctx.send(to_send)
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
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
#check if admin
#only in dm_channel or submission channels
async def _success(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.author.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    if ctx.channel.id not in subm.values() or not isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.author.send(f"{ctx.author.mention}. This command only allowed in submission channels or DM"); return
    content = arg.split(" ", 2)
    if len(content) < 2:
        await ctx.author.send("Not enough information"); return
    psetid = content[0].lower(); memberid = content[1]; numbers = [] if len(content)==2 else re.findall("\d+", content[2])
    topic = db.execute("SELECT topic FROM ? WHERE psetID=?", f"a{memberid}", psetid)
    if len(topic) == 0: 
        await ctx.author.send("Invalid (PsetID not matched memberID)"); return
    topic = topic[0]['topic']
    if subm[topic] != ctx.channel.id:
        await ctx.author.send(f"Wrong channel for this topic {topic}. Try again in the right one."); return
    try:
        numbers = map(extra.check_number_pset, numbers)
        numbers = [num for num in numbers if num is not None]
    except: await ctx.author.send("Invalid problem numbers"); return
    if len(content) > 2 and len(numbers) == 0:
        await ctx.author.send(f'{ctx.author.mention}. We suspect that u did smt wrong in sending numbers that the student solved.\
                       \nUr numbers should be in the format 1 3 4 for example'); return
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} checked: {ctx.message}")
    await ctx.message.pin()
    problemid = db.execute("SELECT p1, p2, p3, p4, p5 FROM psets WHERE psetID=?", psetid)[0]
    for num in range(1,6):
        if num not in numbers: 
            problemid.pop(f'p{num}')
    index = toi[topic]
    member_rating = eval(db.execute("SELECT m_rating FROM members WHERE memberID=?", memberid)[0]['m_rating'])
    for id in problemid:
        problem = db.execute("SELECT topic, p_rating FROM problems WHERE problemID=?", id)[0]
        if_hint = db.execute("SELECT hints_used FROM ? WHERE solving=?", f"{topic}{id}", memberid)[0]['hints_used']
        if problem['p_rating'] > member_rating[index]:
            added = (problem['p_rating'] - member_rating[index])/5 
            if if_hint: added /= 4
            member_rating[index] += added
        db.execute("UPDATE ? SET success=1, checked_by=? WHERE solving=?", f"{topic}{id}", ctx.author.id, memberid) 
    db.execute("UPDATE members SET m_rating=? WHERE memberID=?", member_rating, memberid) 
    return

#psetid 
@bot.command(name="pset_checked_ask")
@commands.dm_only()
async def _pset_checked_ask(ctx, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role to use this command"); return
    memberid = db.execute("SELECT memberID FROM psets WHERE psetID=?", arg)
    if not len(memberid):
        await ctx.send("Invalid psetid"); return
    memberid = memberid[0]['memberID']
    submitted = db.execute("SELECT sub_time FROM ? WHERE psetID=?", f"a{memberid}", arg)[0]['sub_time']
    to_send = f"{ctx.author.mention}. Pset {arg} is" + (" " if submitted else " not ") + "done checking."
    await ctx.send(to_send)
    return

###memberid psetid followed by string of feedback
@bot.command(name="feedback_give")
@commands.dm_only()
async def _feedback_give(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!")
        return
    content = arg.split(" ", 2)
    mid, pid, feedback = (i for i in content)
    if not len(db.execute("SELECT psetID FROM ? WHERE psetID=?", f"a{mid}", pid.lower())):
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
        rating = float(rating); source = extra.check_source(source); topic = extra.check_topic(topic)
    except: await ctx.send("Invalid rating"); return
    if not source or len(db.execute("SELECT * FROM problems WHERE problemID=?", source)): 
        await ctx.send("Invalid problem source or already exists."); return
    if not topic:
        await ctx.send("Invalid topic"); return
    db.execute("INSERT INTO problems (problemID, problem_statement, topic, p_rating) VALUES (?, ?, ?, ?)", source, problem, topic, rating)
    db.execute("INSERT INTO hints (problemID) VALUES (?)", source)
    db.execute("CREATE TABLE IF NOT EXISTS ? (solving TEXT PRIMARY KEY, hints_used INTEGER DEAFULT 0, \
               success INTEGER DEFAULT 0, checked_by TEXT)", f"{topic}{source}")
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} added a new problem {source} themed in {topic} rated {rating}")
    return

#problemID topic
@bot.command(name="problem_delete")
@commands.dm_only()
async def _problem_delete(ctx, id, topic):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    id = id.lower()
    topic = extra.check_topic(topic)
    if not len(db.execute("SELECT problemID FROM problems WHERE problemID=? AND topic=?", id, topic)):
        await ctx.send(f"Invalid problemID or topic"); return
    db.execute("DELETE FROM problemID WHERE problemID=? AND topic=?", id, topic)
    db.execute("DROP TABLE IF EXISTS ?", f"{topic}{id}")
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} deleted a problem {id} themed in {topic}")
    return

#problem_id tag tag tag ...
@bot.command(name="problem_tagged")
@commands.dm_only()
async def _problem_tagged(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You dont have the role for this command!"); return
    content = arg.lower().split(" ")
    if len(content) < 2: 
        await ctx.send(f"Not enough information!"); return
    problemid = content[0]; tags = content[1:]
    problem = db.execute("SELECT * FROM problems WHERE problemID = ?", problemid)
    if not len(problem):
        await ctx.send(f"{ctx.author.mention}. Invalid problem ID"); return
    channel = await bot.fetch_channel(JURY); to_send = f"{ctx.author.mention} tagged {problemid}"
    for tag in tags:
        tag_topic = db.execute("SELECT topic FROM tags WHERE name = ?", tag)
        if len(tag_topic):
            db.execute("INSERT INTO ? (problemID, p_rating) VALUES (?, ?))",\
                        f"{tag_topic[0]['topic']}{tag}", problemid, problem[0]['p_rating'])
            to_send += f" {tag} "
    await channel.send(to_send)
    return

#problemID
@bot.command(name="problem_get")
@commands.dm_only()
async def _problem_get(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    content = db.execute("SELECT problem_statement from problems WHERE problemID=?", arg.lower().strip())
    if not len(content): 
        await ctx.send("Invalid problemID"); return
    content = content[0]['problem_statement']
    await ctx.send(content)
    return

#problemID hint_no. followed by hint
@bot.command(name="hint_add")
@commands.dm_only()
#check if admin
async def _hint_add(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    content = arg.split(" ", 2)
    if len(content) <3:
        await ctx.send("Not enough information")
    try:
        if not len(db.execute("SELECT problemID FROM hints WHERE problemID=?", content[0])):
            await ctx.send("Invalid problemID (doesnt exists)"); return
        problemID = content[0].lower(); hint_no = int(content[1]); hint = content[2]
        if hint_no >3 or hint_no <1: 
            raise Exception
        hint_no = f"hint_{hint_no}"
    except: await ctx.send("Invalid hint no. (integer only allowed from 1 to 3)"); return
    if db.execute("SELECT ? FROM hints WHERE problemID=?", hint_no, problemID)[0][hint_no]:
        await ctx.send(f"{hint_no} already exists. Use hint_overwrite command to modify the hint"); return
    db.execute("UPDATE hints SET ? = ?", hint_no, hint)
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} added {hint_no} to {problemID}")
    return

@bot.command(name="hint_overwrite")
@commands.dm_only()
#check if admin
async def _hint_overwrite(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    content = arg.split(" ", 2)
    if len(content) < 2:
        await ctx.send("Not enough information")
    try:
        if not len(db.execute("SELECT problemID FROM hints WHERE problemID=?", content[0])):
            await ctx.send("Invalid problemID (doesnt exists)"); return
        problemID = content[0].lower(); hint_no = int(content[1]); hint = "" if len(content)==2 else content[2]
        if hint_no >3 or hint_no <1: 
            raise Exception
        hint_no = f"hint_{hint_no}"
    except: await ctx.send("Invalid hint no. (integer only allowed from 1 to 3)"); return
    old_hint = db.execute("SELECT ? FROM hints WHERE problemID=?", hint_no, problemID)[0][hint_no]
    old_hint = old_hint if old_hint else "empty"
    await ctx.send(f"The prev hint u intend to overwrite is {old_hint}")
    db.execute("UPDATE hints SET ? = ?", hint_no, hint)
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} added {hint_no} to {problemID}")
    return

#tag_name topic
@bot.command(name='tag_add')
@commands.dm_only()
@commands.is_owner()
async def _tag_add(ctx, name, topic: extra.check_topic):
    if not topic: 
        await ctx.send("Invalid topic"); return
    name = name.lower(); topic = extra.check_topic(topic)
    db.execute("INSERT INTO tags (name, topic) VALUES (?, ?)", name, topic)
    db.execute("CREATE TABLE IF NOT EXISTS ? (problemID TEXT PRIMARY KEY, p_rating REAL,\
           CONSTRAINT constraint_tag FOREIGN KEY (problemID) REFERENCES problems(problemID) ON DELETE CASCADE)", f"{topic}{name}")
    jury = await bot.fetch_channel(JURY)
    await jury.send(f"{ctx.author.mention} added new tag: {name} in topic: {topic}")
    return

@bot.command(name="tag_delete")
@commands.is_owner()
@commands.dm_only()
async def _tag_delete(ctx, name, topic: extra.check_topic):
    if not topic:
        await ctx.send("Invalid topic"); return
    name = name.lower(); topic = extra.check_topic(topic)
    db.execute("DELETE FROM tags WHERE name=? AND topic=?", name, topic)
    db.execute("DROP TABLE IF EXISTS ?", f"{topic}{name}")
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
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command"); return
    content = arg.split(" ", 2)
    if len(content) < 2:
        await ctx.send("Not enough information"); return
    if len(db.execute("SELECT memberID FROM members WHERE memberID=?", content[0])) == 0:
        await ctx.send("Invalid Member ID"); return
    try: content[1] = int(content[1])
    except: await ctx.send("1 for approval, 0 for disapproval"); return
    user = await bot.fetch_user(int(content[0])); response = content[2]
    jury = await bot.fetch_channel(JURY); a = "" if content[1] else "not"
    to_send = f"{ctx.author.mention} did {a} approve a problem."
    await jury.send(to_send)
    await user.send(f"{to_send}.\n{response}")
    await ctx.send(f"{ctx.author.mention}. Make sure u added the latex'd version of problem and necessaries if approved.\
                   \nAfter that, ensure to delete the message of original problem proposal that you handled, to stay clean!!!")
    await ctx.author.send("problemID should be in the format [proposer_name][proposed_year][p][(n+1)_if_user_had_n_approvals]")
    num = db.execute("SELECT number FROM approved WHERE memberID=?", content[0])[0]['number']
    await ctx.author.send(f"This user previously had {num} approvals")
    db.execute("UPDATE approved SET number = number + 1 WHERE memberID = ?", content[0])

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
