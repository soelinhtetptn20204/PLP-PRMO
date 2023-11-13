"""
import json, os, time
import pandas as pd
"""
import spacy
import re
from difflib import SequenceMatcher
"""
from cs50 import SQL
db = SQL("sqlite:///test.db")

for tag in TAGS:
    db.execute("INSERT INTO tags (name, topic) VALUES (?, ?)", tag, TAGS[tag])
    db.execute("CREATE TABLE IF NOT EXISTS ? (problemID TEXT PRIMARY KEY, p_rating REAL,\
           CONSTRAINT constraint_tag FOREIGN KEY (problemID) REFERENCES problems(problemID) ON DELETE CASCADE)", f"{TAGS[tag]}{tag}")
"""
NER = spacy.load("model-last-10-nov")

with open("tags.txt") as f:
    tags = [tag.strip() for tag in f]

numbers = {"one": "1", "two": "2", "three": "3",
           "four": "4", "five": "5", "six":"6",
           "seven": "7", "eight": "8", "nine": "9"}

TAGS = {
    'geometry': 'g', 'number_theory': 'n', 'combinatorics': 'c', 'algebra': 'a',
    'invariant': 'c', 'c_induction': 'c', 'pigeonhole': 'c', 'invariant': 'c','monovariant': 'c','greedy': 'c', 'graph_theory': 'c', 'counting': 'c', 'permutation': 'c','rust': 'c',
    'n_induction': 'n', 'divisibility':'n','gcd-lcm':'n','prime':'n','fermat':'n','modulo':'n',
    'a_induction': 'a', 'am-gm':'a', 'cauchy':'a', 'polynomial':'a', 'inequality':'a', 'harmonic_mean':'a', 'functional_equation':'a',
    'angle_chasing': 'g', 'incenter':'g',  'lengths':'g', 'cyclic_quad':'g', 'orthocenter':'g', 'sprial_sim':'g', 'similarity':'g'
}

def check_tag (inputStr):
    Max = SequenceMatcher(a = tags[0], b = inputStr).ratio()
    index = 0
    for i in range(len(tags)):
        percent = SequenceMatcher(a = tags[i], b = inputStr).ratio()
        if percent > Max:
            Max = percent
            index = i
    if Max > 0.7:
        return [tags[index]]
    elif inputStr == 'fe':
        return ["functional_eq"]
    elif inputStr == 'nt':
        return ["number_theory"]
    elif len(inputStr) <= 7:
        return [tags[index]]
    return []
    

def ratings (string, order):
    normal_list = re.findall('\d+\.\d+', string)
    for i in normal_list: string.replace(i, "")
    normal_list += re.findall('\d+', string)
    normal_list = [round(float(number)) for number in normal_list]
    if order == "RANGE":
        start = min(normal_list)
        end = max(normal_list)
        if start < 2 or end > 4:
            return []
        else:
            return list(range(start, end+1))
    elif order == "RATING":
        normal_list =  list(set(normal_list))
        if normal_list[0] < 2 or normal_list[len(normal_list)-1] >4:
            return []
        else:
            return normal_list

def check_topic(txt):
    #since this function will be used by high lvl users such as admins more often
    tags = {'geometry':'g', 'geo':'g', 'g':'g',
            'algebra':'a', 'alge':'a', 'a':'a',
            'number_theory':'n', 'nt':'n', 'n':'n',
            'combinatorics':'c', 'combi':'c', 'c':'c'} #tags
    med = txt.strip().lower()
    return tags[med] if med in tags else 0

def check_source(txt):
    #the format of a problem ID is
    #{abbr}{year in 4 digit after 1959}p{integer}
    #return original string if valid, false otherwise
    return txt.lower()

def check_number_pset(number):
    number = int(number)
    if number >=1 and number <=5:
        return number
    else: return

def text_transform(text):
    for number in numbers:
        text = text.replace(number, f" {numbers[number]} ")
    return text.replace("  ", " ").strip()

def NLP(content):
    """
    to retrain the model for "about/around" on quantity of problems
    """
    text = NER(text_transform(content))
    entities =  {'TOPIC': {'a':0, 'c':0, 'g':0, 'n':0}, 'TAG':[], 'RATING':[], 'QUANTITY':0}
    for word in text.ents:
        if word.label_ in ['RANGE', 'RATING']:
            entities['RATING'] += ratings(word.text)
        elif word.label_ == 'TAG':
            entities['TAG'] += check_tag(word.text)
        else:
            try: quan = 1 if word.text.strip() in ['a','an'] else int(word.text)
            except: quan = 0
            entities['QUANTITY'] += quan
    for tag in entities['TAG']:
        entities['TOPIC'][TAGS[tag]]+=1
    entities['TOPIC'] = max(entities['TOPIC'], key=entities['TOPIC'].get)
    return entities

"""
from cs50 import SQL
db = SQL("sqlite:///test.db")
a = db.execute("SELECT MAX(id) FROM testing")[0]
print(a)

TEMPORARY
@bot.command(name="recommend", help="Just uses $recommend in DM")
@commands.max_concurrency(1,per=commands.BucketType.default,wait=False)
#@commands.cooldown(1, 250, commands.BucketType.default)
async def _recommend(ctx):
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
"""