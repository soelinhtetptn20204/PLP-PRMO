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
import re, random
from database import db
from table2ascii import table2ascii as t2a, PresetStyle
from copy import deepcopy

WEEKLY_LEADERBOARD = 0000

#channel names/id will change
ANNOUNCEMENT = 0000
RULES = 0000
ENTRIES = 0000
PROPOSAL = 0000
JURY = 0000

HINT_THREAD = 0000
TAG_THREAD = 0000
PROBLEM_THREAD = 0000

subm = {
"a": 0000,
"c": 0000,
"g": 0000,
"n": 0000
}

toi = { 'a': 0,'c': 1,'g': 2,'n': 3 }
iot = { 0:'a', 1:'c', 2:'g', 3:'n' }

ratings = {
    'ADMIN': 4,
    'IMO-er': 4,
    'TST': 3,
    'MOMC_Sr': 2.5,
    'MOMC_Jr': 2
}
"""
TAGS = {
    'geometry': 'g', 'number_theory': 'n', 'combinatorics': 'c', 'algebra': 'a',
    'invariant': 'c', 'c_induction': 'c', 'pigeonhole': 'c', 'invariant': 'c','monovariant': 'c','greedy': 'c', 'graph_theory': 'c', 'counting': 'c', 'permutation': 'c','rust': 'c',
    'n_induction': 'n', 'divisibility':'n','gcd-lcm':'n','prime':'n','fermat':'n','modulo':'n',
    'a_induction': 'a', 'am-gm':'a', 'cauchy':'a', 'polynomial':'a', 'inequality':'a', 'harmonic_mean':'a', 'functional_equation':'a',
    'angle_chasing': 'g', 'incenter':'g',  'lengths':'g', 'cyclic_quad':'g', 'orthocenter':'g', 'sprial_sim':'g', 'similarity':'g'
}"""

now = datetime.now()
#errors
with open("error_code.txt") as f:
    errors = f.read()
errors = json.loads(errors)
B = 'b'
FORMAT = r"\begin{center}" + "\n" + "{\large Pset id - topic}\n\end{center}\n" + r"\begin{enumerate}" + "\n"

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

def leaderboard(body= []):
    output = t2a(header=["Name", "Points"],
                body=body,
                style=PresetStyle.thin_compact)
    return output

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
    db.execute("CREATE TABLE IF NOT EXISTS ? (psetID INTEGER PRIMARY KEY, topic TEXT, sub_time TEXT,\
               CONSTRAINT constraint_hint FOREIGN KEY (problemID) REFERENCES problems(problemID) ON DELETE CASCADE)", f"a{member.id}")
    db.execute("INSERT INTO approved (memberID, number) VALUES (?, 0)", member.id)
    ###create each user table foreign key included
    channel = bot.get_channel(ENTRIES)
    await channel.send(f"Please welcome {member.mention}.\
                       \nEnjoy problem solving!")
    return

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
    return

@bot.event 
async def on_member_remove(member):
    db.execute("UPDATE members SET activated=0 WHERE memberID=?", member.id)
    return

#conversational msg
@bot.command(name="hey")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def recommend(ctx, *, content):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server to req problems"); return
    entities = extra.NLP(content.strip().lower())
    print(entities)
    if not len(entities['TAG']) or not entities['QUANTITY']: 
        await ctx.send("You must specify which topic/theme and quantity u want to do, or u can msg just '$recommend' for\
                        random problem recommendation depending on ur previous askings"); return
    topic = entities.pop('TOPIC')
    ratings = entities['RATING'] if entities['RATING'] else [eval(db.execute("SELECT m_rating FROM members WHERE memberID=?",
                                                                            ctx.author.id)[0]['m_rating'])[toi[topic]]]
    tags = entities['TAG']; quan = entities["QUANTITY"]
    problemID = {}
    for tag in tags:
        if db.execute("SELECT name FROM tags WHERE name=? AND topic=?", tag, topic):
            for rating in ratings:
                id = db.execute("SELECT problemID FROM ? WHERE p_rating=?", f"{topic}{tag}", rating)
                for i in id:
                    pid = i['problemID']
                    if db.execute("SELECT solving FROM ? WHERE solving=?", f"{topic}{pid}", ctx.author.id):
                        continue
                    if pid not in problemID: 
                        problemID[pid] = 2.5
                    else: problemID[i] += 1
    problemID = sorted(problemID, key=problemID.get, reverse=1)[0: min(quan, len(problemID))]
    #print(problemID)
    psetid = db.execute("SELECT COUNT(psetID) FROM psets")[0]['COUNT(psetID)'] + 1
    #print(psetid)
    to_send = FORMAT.replace('id', str(psetid)).replace('topic', topic.upper())
    #print(f"iD: {problemID}\npsetid: {psetid}\nto_send:{to_send}")
    if not problemID: 
        await ctx.send("No suitable problems"); return
    for i in problemID:
        subsitute = db.execute("SELECT problem_statement FROM problems WHERE problemID=?", i)[0]['problem_statement']
        to_send += f"\item {subsitute}\n"
    #print(to_send)
    to_send += "\end{enumerate}"
    req_time = now.strftime("%d/%m/%Y, %H:%M")
    await ctx.send(to_send)
    db.execute("INSERT INTO psets (topic, memberID, req_time) VALUES (?,?,?)", topic, ctx.author.id, req_time)
    db.execute("INSERT INTO history (memberID, topic, rating, counts) VALUES (?, ?, ?, ?)", ctx.author.id, topic, ratings, quan)
    for i in range(1, len(problemID)+1):
        db.execute("UPDATE psets SET ? = ? WHERE psetID = ?", f"p{i}", problemID[i-1], psetid)
        db.execute("INSERT INTO ? (solving) VALUES (?)", f"{topic}{problemID[i-1]}", ctx.author.id)
    return

#command fun or improve
@bot.command(name = "recommend")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def recommend(ctx, *, arg):
    ### AUTO RECOMMEND WITHOUT ANY PROMPT ###
    if not member_valid(ctx.author):
        await ctx.send("Please rejoin the server to req problems"); return
    keyword = arg.lower().strip()
    if keyword not in ['fun', 'improve']:
        keyword = 'fun'
    data = db.execute("SELECT topic, rating, counts FROM history WHERE memberID = ?", ctx.author.id)
    if len(data) < 20: 
        await ctx.send("Not enough data to recommend you. You should still use $hey with specific details"); return
    if keyword=='fun': 
        rating={'a':[],'c':[],'g':[],'n':[]}
        topic = []; counts = deepcopy(rating)
        for i in data:
            topic.append(i['topic'])
            rating[i['topic']].append(eval(i['rating']))
            counts[i['topic']].append(i['counts'])
        topic = random.choice(topic)
        quan = random.choice(counts[topic])
        ratings = random.choices(rating[topic], k=quan)
    else:
        rating = db.execute("SELECT m_rating FROM members WHERE memberID=?", ctx.author.id)
        rating = eval(rating[0]['m_rating'])
        topic = iot[rating.index(min(rating))]
        ratings = [max(math.ceil(min(rating)), 2)]
        quan = 4
    #print(ratings, topic, quan)
    tags = db.execute("SELECT name FROM tags WHERE topic=?", topic)[0]['name']
    """
    db.execute("INSERT INTO history (memberID, topic, rating, counts) VALUES (?, ?, ?, ?)", ctx.author.id, topic, ratings, quan)
    problemID = {}
    for tag in tags:
        if db.execute("SELECT name FROM tags WHERE name=? AND topic=?", tag, topic):
            for rating in ratings:
                id = db.execute("SELECT problemID FROM ? WHERE p_rating=?", f"{topic}{tag}", rating)
                for i in id:
                    pid = i['problemID']
                    if db.execute("SELECT solving FROM ? WHERE solving=?", f"{topic}{pid}", ctx.author.id):
                        continue
                    if pid not in problemID: 
                        problemID[pid] = 2.5
                    else: problemID[i] += 1
    problemID = sorted(problemID, key=problemID.get, reverse=1)[0: min(quan, len(problemID))]
    psetid = db.execute("SELECT MAX(psetID) FROM psets")[0]['MAX(psetID)'] + 1
    to_send = FORMAT.replace('id', psetid).replace('topic', topic.upper())
    if not problemID: 
        await ctx.send("No suitable problems"); return
    for i in problemID:
        to_send += f"\item {i}\n"
    req_time = now.strftime("%d/%m/%Y, %H:%M")
    db.execute("INSERT INTO psets (topic, memberID, req_time) VALUES (?,?,?)", topic, ctx.author.id, req_time)
    for i in range(1, quan+1):
        db.execute("UPDATE psets SET ? = ? WHERE problemID = ?", f"p{i}", problemID[i-1], psetid)
        db.execute("INSERT INTO ? (solving) VALUES (?)", f"{topic}{problemID[i-1]}", ctx.author.id)
    await ctx.send(to_send)
    """
    problemID = {}
    for tag in tags:
        if db.execute("SELECT name FROM tags WHERE name=? AND topic=?", tag, topic):
            for rating in ratings:
                id = db.execute("SELECT problemID FROM ? WHERE p_rating=?", f"{topic}{tag}", rating)
                for i in id:
                    pid = i['problemID']
                    if db.execute("SELECT solving FROM ? WHERE solving=?", f"{topic}{pid}", ctx.author.id):
                        continue
                    if pid not in problemID: 
                        problemID[pid] = 2.5
                    else: problemID[i] += 1
    problemID = sorted(problemID, key=problemID.get, reverse=1)[0: min(quan, len(problemID))]
    #print(problemID)
    psetid = db.execute("SELECT COUNT(psetID) FROM psets")[0]['COUNT(psetID)'] + 1
    #print(psetid)
    to_send = FORMAT.replace('id', str(psetid)).replace('topic', topic.upper())
    #print(f"iD: {problemID}\npsetid: {psetid}\nto_send:{to_send}")
    if not problemID: 
        await ctx.send("No suitable problems"); return
    for i in problemID:
        subsitute = db.execute("SELECT problem_statement FROM problems WHERE problemID=?", i)[0]['problem_statement']
        to_send += f"\item {subsitute}\n"
    #print(to_send)
    to_send += "\end{enumerate}"
    req_time = now.strftime("%d/%m/%Y, %H:%M")
    await ctx.send(to_send)
    db.execute("INSERT INTO psets (topic, memberID, req_time) VALUES (?,?,?)", topic, ctx.author.id, req_time)
    db.execute("INSERT INTO history (memberID, topic, rating, counts) VALUES (?, ?, ?, ?)", ctx.author.id, topic, ratings, quan)
    for i in range(1, len(problemID)+1):
        db.execute("UPDATE psets SET ? = ? WHERE psetID = ?", f"p{i}", problemID[i-1], psetid)
        db.execute("INSERT INTO ? (solving) VALUES (?)", f"{topic}{problemID[i-1]}", ctx.author.id)
    return

#psetID followed by a single file
@bot.command(name="submit", help="$submit psetID followed by the image all at once")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def _submit(ctx, arg1: str, arg2: discord.Attachment):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server for submission")
        return
    top = 'a'; arg1 = arg1.lower()
    top = db.execute("SELECT topic FROM ? WHERE psetID = ?", f"a{ctx.author.id}", arg1)
    if len(top) == 0:
        await ctx.send("Invalid pset ID. Try again. $submit psetID followed by the image all at once")
        return 
    top = top[0]['topic']
    now = datetime.now.strftime("%d/%m/%Y, %H:%M")
    db.execute("UPDATE ? SET sub_time=? WHERE psetID=?", f"a{ctx.author.id}", {now}, arg1)
    channel = await bot.fetch_channel(subm[top])
    await channel.send(f"{arg2.url.split('?')[0]}\
                       \npsetID: {arg1}, submittor: {ctx.author.mention}")
    await ctx.send(f"{ctx.author.mention}. Success! Make sure u sent only one attachment.\
                   \nIf not, we recommend scanning all images, combining into a pdf, and sending again.")
    return

#psetid number
@bot.command(name="problem_submit")
@commands.dm_only()
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
async def _problem_submit(ctx, psetid, number, file: discord.Attachment):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server for submission"); return
    try: 
        number = extra.check_number_pset(number)
        problem = db.execute("SELECT topic, ? FROM psets WHERE psetID=?", f"p{number}", psetid)
    except: await ctx.send("Invalid number"); return
    if not problem:
        await ctx.send("Invalid psetID"); return
    id, topic = problem[0][f'p{number}'], problem[0]['topic']
    checked = db.execute("SELECT checked_by FROM ? WHERE memberID=?", f'{topic}{id}', ctx.author)
    if not checked:
        await ctx.send("Using this command, you can only submit problems that failed initially"); return
    now = datetime.now.strftime("%d/%m/%Y, %H:%M")
    db.execute("UPDATE ? SET sub_time=? WHERE psetID=?", f"a{ctx.author.id}", {now}, id)
    channel = await bot.fetch_channel(subm[topic])
    await channel.send(f"{file.url.split('?')[0]}\
                       \npsetID: {id} Number: {number}, submittor: {ctx.author.name}")
    await ctx.send(f"{ctx.author.mention}. Success! Make sure u sent only one attachment.\
                   \nIf not, we recommend scanning all images, combining into a pdf, and sending again.")
    return

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
    to_send = FORMAT.replace('id', arg).replace('topic', topic.upper())
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
async def _companion_match(ctx, arg: None):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server for this service"); return
    if arg is None:
        await ctx.send("Invalid topic")
    topic = extra.check_topic(arg)
    if not topic: 
        await ctx.send("Invalid topic"); return
    topic = toi[topic]
    user = np.array(eval(db.execute("SELECT m_rating FROM members WHERE memberID=?", ctx.author.id)[0]['m_rating']))
    members = db.execute("SELECT memberID, m_rating FROM members WHERE memberID <> ?", ctx.author.id)
    all_round = {int(member['memberID']): np.array(eval(member['m_rating'])) for member in members}
    members = {member: sum(abs(all_round[member]-user))+(all_round[member][topic]-user[topic])**2 for member in all_round}
    matched = min(members, key=members.get)
    user = await bot.fetch_user(matched)
    await ctx.send(f"{user.mention} is the closet match")
    await user.send(f"{ctx.author.mention} is looking a partner for problem solving and ur the closet match")
    return
    
##just the command
@bot.command(name="rating_get")
@commands.dm_only()
async def _rating_get(ctx):
    if not member_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. Please rejoin the server for this service"); return
    rating = eval(db.execute("SELECt m_rating FROM members WHERE memberID=?", ctx.author.ID)[0]['m_rating'])
    await ctx.send(f"Your ratings for [a, c, g, n] rn are {rating}")
    return

###psetid memberid followed by numbers successful
@bot.command(name="success")
@commands.max_concurrency(1, per=commands.BucketType.default,wait=False)
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
    med = {key: (problemid[key], 0) for key in problemid if problemid[key]}
    for num in range(1,6):
        if num in numbers:
            med[f'p{num}'] = (med[f'p{num}'][0], 1)
    index = toi[topic]
    member_rating = eval(db.execute("SELECT m_rating FROM members WHERE memberID=?", memberid)[0]['m_rating'])
    for id, success in med.values():
        problem = db.execute("SELECT topic, p_rating FROM problems WHERE problemID=?", id)[0]
        if_hint = db.execute("SELECT hints_used FROM ? WHERE solving=?", f"{topic}{id}", memberid)[0]['hints_used']
        if problem['p_rating'] > member_rating[index]:
            added = (problem['p_rating'] - member_rating[index])/5 
            if if_hint: added /= 4
            member_rating[index] += added
        db.execute("UPDATE ? SET success=?, checked_by=? WHERE solving=?", f"{topic}{id}", success, ctx.author.id, memberid) 
        if success:
            db.execute("UPDATE leaderboard SET points = points + ? WHERE memberID=?", problem['p_rating']**1.5)
    db.execute("UPDATE members SET m_rating=? WHERE memberID=?", member_rating, memberid) 
    body = db.execute("SELECT * FROM leaderboard ORDER BY points DESC LIMIT 10")
    med = []
    for i in body:
        user = await bot.fetch_user(int(i['memberID']))
        med.append([user.name, i['points']])
    data_table = leaderboard(med)
    msg = await bot.fetch_channel(ANNOUNCEMENT)
    msg = await msg.fetch_message(WEEKLY_LEADERBOARD)
    await msg.send(f"{data_table}")
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
    pid = db.execute("SELECT p1, topic FROM psets WHERE psetID=?", arg)[0]
    pid, topic = pid['p1'], topic['topic']
    checked = db.execute("SELECT checked_by FROM ? WHERE memberID=?", f"{topic}{pid}", ctx.author.id)[0]['checked_by']
    to_send = f"{ctx.author.mention}. Pset {arg} is" + (" " if checked else " not ") + "done checking."
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
    if len(content) < 4: 
        await ctx.send(f"{ctx.author.mention}. Not enough information for a problem"); return
    try: 
        source, rating, topic, problem = (i for i in content)
        rating = float(rating); source = source.lower().strip(); topic = extra.check_topic(topic); problem=problem.strip()
    except: await ctx.send("Invalid rating"); return
    if len(db.execute("SELECT * FROM problems WHERE problemID=? OR problem_statement=?", source, problem)): 
        await ctx.send("Invalid problem source or already exists."); return
    #print(content)
    if topic == 0:
        await ctx.send("Invalid topic"); return
    db.execute("INSERT INTO problems (problemID, problem_statement, topic, p_rating) VALUES (?, ?, ?, ?)", source, problem, topic, rating)
    db.execute("INSERT INTO hints (problemID) VALUES (?)", source)
    #print(content)
    db.execute("CREATE TABLE ? (solving TEXT PRIMARY KEY, hints_used INTEGER DEFAULT 0, success INTEGER DEFAULT 0, checked_by TEXT,\
               CONSTRAINT constraint_each FOREIGN KEY (solving) REFERENCES members (memberID) ON DELETE CASCADE)", f"{topic}{source}")
    jury = await bot.fetch_channel(JURY)
    thread = jury.get_thread(PROBLEM_THREAD)
    await thread.send(f"{ctx.author.mention} added a new problem *{source}* themed in {topic.upper()} rated {rating}")
    return

#problemID topic
@bot.command(name="problem_delete")
@commands.max_concurrency(1, per=commands.BucketType.default,wait=False)
@commands.dm_only()
async def _problem_delete(ctx, id, topic):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    id = id.lower()
    topic = extra.check_topic(topic)
    pstatement = db.execute("SELECT problem_statement FROM problems WHERE problemID=? AND topic=?", id, topic)
    if not len(pstatement):
        await ctx.send(f"Invalid problemID or topic"); return
    pstatement = pstatement[0]['problem_statement']
    db.execute("DELETE FROM problems WHERE problemID=? AND topic=?", id, topic)
    db.execute("DROP TABLE IF EXISTS ?", f"{topic}{id}")
    jury = await bot.fetch_channel(JURY)
    thread = jury.get_thread(PROBLEM_THREAD)
    await thread.send(f"{ctx.author.mention} deleted a problem {id} themed in {topic.upper()}\
                    \nThe problem statement of the deleted problem: {pstatement}")
    return

#psetID
@bot.command(name="pset_delete")
@commands.dm_only()
async def _pset_delete(ctx, psetID):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mentio}. You dont have the role for this command"); return
    psetID = id.lower().strip()
    if not db.execute("SELECT psetID FROM psets WHERE psetID=?", psetID):
        await ctx.send(f"Invalid PsetID"); return
    db.execute("DELETE FROM psets WHERE psets WHERE psetID=?", psetID)
    return

#problem_id tag tag tag ...
@bot.command(name="problem_tagged")
@commands.max_concurrency(1, per=commands.BucketType.default,wait=False)
@commands.dm_only()
async def _problem_tagged(ctx, *, arg):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You dont have the role for this command!"); return
    content = arg.lower().split(" ")
    if len(content) < 2: 
        await ctx.send(f"Not enough information!"); return
    problemid = content[0]; med = content[1:]; tags = []
    for tag in med:
        tags += extra.check_tag(tag)
    problem = db.execute("SELECT * FROM problems WHERE problemID = ?", problemid)
    if not len(problem):
        await ctx.send(f"{ctx.author.mention}. Invalid problem ID"); return
    channel = await bot.fetch_channel(JURY); thread = channel.get_thread(PROBLEM_THREAD)
    to_send = f"{ctx.author.mention} tagged {problemid}"
    for tag in tags:
        tag_topic = db.execute("SELECT topic FROM tags WHERE name = ?", tag)
        if len(tag_topic):
            db.execute("INSERT INTO ? (problemID, p_rating) VALUES (?, ?)", 
                       f"{tag_topic[0]['topic']}{tag}", problemid, problem[0]['p_rating'])
            to_send += f" {tag} "
    await thread.send(to_send)
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

#problemID topic new_rating
@bot.command(name="rating_change")
@commands.dm_only()
async def _rating_change(ctx, pid, topic, new_rating):
    if not admin_valid(ctx.author):
        await ctx.send(f"{ctx.author.mention}. You don't have the role for this command!"); return
    topic = extra.check_topic(topic); pid = pid.lower().strip()
    if not db.execute("SELECT problemID FROM problems WHERE problemID=?", pid): 
        await ctx.send("Invalid problemID"); return
    try: new_rating = float(new_rating)
    except: await ctx.send("Invalid rating"); return
    possible_tags = db.execute("SELECT name FROM tags WHERE topic=?", topic)
    if not possible_tags: await ctx.send("Invalid topic"); return
    for i in possible_tags:
        db.execute("UPDATE ? SET p_rating=? WHERE problemID=?", f"{topic}{i['name']}", new_rating, pid)
    db.execute("UPDATE problems SET p_rating=? WHERE problemID=?", new_rating, pid)
    jury = await bot.fetch_channel(JURY)
    thread = jury.get_thread(PROBLEM_THREAD)
    await thread.send(f"{ctx.author.mention} changed the rating of the problem {pid} to {new_rating}")
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
    thread = jury.get_thread(HINT_THREAD)
    await thread.send(f"{ctx.author.mention} added {hint_no} to {problemID}")
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
    thread = jury.get_thread(HINT_THREAD)
    await thread.send(f"{ctx.author.mention} changed {hint_no} of {problemID} from {old_hint} to {hint}")
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
    thread = jury.get_thread(TAG_THREAD)
    await thread.send(f"{ctx.author.mention} added new tag: {name} in topic: {topic}")
    return

#tag_name topic
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
    thread = jury.get_thread(TAG_THREAD)
    await thread.send(f"{ctx.author.mention} deleted the tag: {name} in topic: {topic}")
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
    await ctx.author.send(f"{ctx.author.mention}. Make sure u added the latex'd version of problem and necessaries if approved.\
                   \nAfter that, ensure to delete the message of original problem proposal that you handled, to stay clean!!!")
    await ctx.author.send("problemID should be in the format [proposer_name][proposed_year][p][(n+1)_if_user_had_n_approvals]")
    num = db.execute("SELECT number FROM approved WHERE memberID=?", content[0])[0]['number']
    await ctx.author.send(f"This user previously had {num} approvals")
    db.execute("UPDATE approved SET number = number + 1 WHERE memberID = ?", content[0])
    return

@bot.command(name="leaderboard_reset")
@commands.is_owner()
@commands.dm_only()
async def _leaderboard_reset(ctx):
    db.execute("UPDATE leaderboard SET points = 0")
    await ctx.send("Succses resetting")
    return

@bot.command(name="delete_invite_links")
@commands.guild_only()
@commands.has_role("ADMIN")
async def _delete_invite_links(ctx):
    guild = ctx.guild
    for invite in await guild.invites():
        await invite.delete()
    await ctx.send("Done Deleting")
    return

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
